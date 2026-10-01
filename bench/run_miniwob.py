"""Run frozen MiniWoB tasks with the upstream evaluator isolated from the agent.

Uses CDP for normal inputs instead of Selenium. Reports raw success with a
120-second LLM-friendly timeout, not a standard MiniWoB leaderboard score.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from typesafe_sdk import TypeSafeClient

from typesafe_computer_use.browser import act
from typesafe_computer_use.browser.cdp import Chrome
from typesafe_computer_use.browser.orchestrator import run_task
from typesafe_computer_use.browser.report import RunFolder
from typesafe_computer_use.browser.runner import run_goal
from typesafe_computer_use.config import load_dotenv
from typesafe_computer_use.writer import make_writer
from typesafe_computer_use.writer_fallback import from_env


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument("--checkout", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--mode", choices=["reflex", "planned", "adaptive"], required=True)
    ap.add_argument(
        "--split",
        choices=[
            "development",
            "heldout",
            "validation",
            "broad",
            "unseen",
            "repair",
            "generalization",
            "release_validation",
            "final_validation",
            "shipping_validation",
            "stable_validation",
            "completion_validation",
            "stability_repeat",
        ],
        default="development",
    )
    ap.add_argument("--task", default=None)
    ap.add_argument("--rounds", type=int, default=12)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "bench/miniwob-tasks.json").read_text())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.checkout, text=True).strip()
    if commit != manifest["upstream_commit"]:
        raise ValueError("Benchmark checkout does not match frozen manifest")
    for line in (Path.home() / ".env").read_text().splitlines():
        key, _, value = line.partition("=")
        if key.strip() == "TYPESAFE_API_KEY":
            os.environ.setdefault("TYPESAFE_API_KEY", value.strip().strip("\"'"))
    load_dotenv(root / ".env")
    writer = make_writer()
    planner = from_env(planner=True)
    split = manifest[args.split]
    tasks = [args.task] if args.task else split["tasks"]
    if any(task not in split["tasks"] for task in tasks):
        raise ValueError("Task is outside the chosen frozen split")
    batch = args.output / (datetime.now(UTC).strftime("%Y%m%d-%H%M%S") + "-" + args.mode + "-" + args.split)
    batch.mkdir(parents=True, exist_ok=False)
    source_hashes = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((root / "typesafe_computer_use").rglob("*.py"))
    }
    (batch / "manifest.json").write_text(
        json.dumps({**manifest, "mode": args.mode, "source_hashes": source_hashes, "max_planner_rounds": args.rounds}, indent=2)
    )
    print(f"Batch: {batch}", flush=True)
    results = []
    with TypeSafeClient() as client:
        for task in tasks:
            for seed in split["seeds"]:
                folder = batch / f"{task}-{seed}"
                folder.mkdir()
                started = time.perf_counter()
                row = {"task": task, "seed": seed, "pass": False}
                try:
                    with Chrome() as chrome, chrome.attach() as session:
                        session.call(
                            "Emulation.setDeviceMetricsOverride",
                            {"width": 500, "height": 700, "deviceScaleFactor": 1, "mobile": False},
                        )
                        act.navigate(session, (args.checkout / "miniwob/html/miniwob" / (task + ".html")).as_uri())
                        act.wait_for_load(session)
                        session.evaluate(
                            f"Math.seedrandom({json.dumps(str(seed))}); core.EPISODE_MAX_TIME={manifest['episode_timeout_seconds'] * 1000}; core.startEpisodeReal();"
                        )
                        goal = str(session.evaluate("document.querySelector('#query').innerText"))
                        row["goal"] = goal

                        # Evaluator state never enters an agent prompt. Only termination
                        # is used to stop further actions after upstream scores a task.
                        def ended():
                            return session.evaluate("WOB_DONE_GLOBAL") is True

                        if args.mode == "reflex":
                            result = run_goal(
                                session,
                                client,
                                goal,
                                max_steps=manifest["max_steps"],
                                writer=writer,
                                runfolder=RunFolder(folder),
                                stop_when=ended,
                                deadline=time.perf_counter() + manifest["episode_timeout_seconds"],
                            )
                            row.update(outcome=result.outcome, steps=len(result.steps))
                        else:
                            result = run_task(
                                session,
                                client,
                                goal,
                                writer=writer,
                                planner=planner,
                                output=folder,
                                max_steps=manifest["max_steps"],
                                max_rounds=args.rounds,
                                max_seconds=manifest["episode_timeout_seconds"],
                                stop_when=ended,
                                fast_start=args.mode == "adaptive",
                            )
                            row.update(outcome=result["outcome"], steps=result["steps"])
                        grade = session.evaluate(
                            "({done:WOB_DONE_GLOBAL,raw_reward:WOB_RAW_REWARD_GLOBAL,reward:WOB_REWARD_GLOBAL,reason:WOB_REWARD_REASON})"
                        )
                        row.update(grade, **{"pass": bool(grade["done"] and grade["raw_reward"] == 1)})
                        shot = session.call("Page.captureScreenshot", {"format": "png"})
                        (folder / "final.png").write_bytes(base64.b64decode(shot["data"]))
                except Exception as exc:
                    row["error"] = type(exc).__name__
                row["total_ms"] = round((time.perf_counter() - started) * 1000, 1)
                results.append(row)
                (folder / "grade.json").write_text(json.dumps(row, indent=2) + "\n")
                (batch / "results.json").write_text(json.dumps(results, indent=2) + "\n")
                print(json.dumps(row), flush=True)
    print(f"Passed {sum(r['pass'] for r in results)}/{len(results)}; results: {batch}", flush=True)


if __name__ == "__main__":
    main()
