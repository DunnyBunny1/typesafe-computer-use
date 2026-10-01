# Reliability iteration: October 1, 2026

The repository remains a fork of Aaron Levin’s TypeSafe Computer Use. Its fast engine vendors Browser Use Jev Ultrafast under MIT at the pinned upstream commit documented in `_vendor/jev_ultrafast/UPSTREAM.md`. This iteration improves that integration; it is neither a new repository nor a GitHub fork of Jev Ultrafast.

## Objective and protocol

Improve the original 9/12 fast-engine result to 12/12 while retaining low typical latency, then probe additional seeds and task families. Tests use isolated **headless** Chrome on the same Mac and the existing pinned MiniWoB++ checkout, 500 × 700 viewport, 40-action and 120-second budgets. The agent sees rendered content and observed controls. The independent grader requires the upstream terminal flag and raw reward exactly 1; partial credit and self-reported completion are failures. Case times include browser launch, execution and evidence. No grader answers, hidden application variables, benchmark-name dispatch or task-specific target scripts are added to the engine.

All iteration runs are retained. The original 12 families are development cases. Seeds 88009/88010 were initially fresh but later informed fixes. The 20 additional families at seed 88011 likewise became development cases after their first run. First-use checks at seeds 88012 and 88013 exposed further pagination mistakes and subsequently informed the fix. Seed 88014 passed its first-use check before review fixes, then was rerun for release acceptance; it is no longer held out for the released code. These are adapted benchmark measurements, not an official score or proof of arbitrary website or desktop reliability.

## Retained changes

- A numeric result-position constraint excludes known-wrong links using counts from preceding pages actually observed. Uniform-page estimates are never used to exclude an action; a mistaken recovery hint cannot override the original numeric constraint.
- Visible controls now include their selected/current state, nearby text, group positions, ordinary links inside tab panels and autocomplete metadata. Covered controls are excluded before selection.
- The text writer receives other observed field values and paragraph word positions. It can copy or extract from a page without guessing missing context.
- Field input checks target identity and the complete observed context supplied to the text writer, including source paragraphs outside the form. Explicit timers and standalone countdown counters are excluded from writer evidence; changed source fields, amounts and references invalidate the action.
- Nested scroll regions are explicit observed actions, hit-tested before input.
- A DONE claim receives a separate Jev completion check. A live draft-form test checks that explicit “do not submit” remains respected.
- Low-confidence target decisions or action cycles can request up to three short recovery hints. Jev chooses the subsequent observed action. This is occasional recovery, not a planner on every click. The default hint model is GPT-4.1 mini via the configured compatible endpoint; Mercury 2.5 remains the ordinary OpenRouter text writer.
- Each provider request has an eight-second cancellation deadline, including responses that keep emitting heartbeat bytes. Ordinary read timeouts alone did not prevent the observed 121-second stall. Text failures can fall back to other configured providers; credentials remain bound to their own endpoints. No interrupted browser mutation is replayed.

## Final results

| Workload | Pass | Median | p95 |
|---|---:|---:|---:|
| Original 12, seed 88008 | 12/12 | 1.97 s | 10.06 s |
| Two development seeds 88009/88010 | 24/24 | 1.80 s | 6.03 s |
| 20 additional families, seed 88011 | 17/20 | 1.80 s | 7.34 s |
| Rechecked seed 88013 | 12/12 | 1.73 s | 6.68 s |
| Rechecked seed 88014 | 12/12 | 2.16 s | 3.28 s |

The original 12 improved from **9/12 to 12/12** (+25 percentage points); median time increased from **1.66 to 1.97 seconds** as verification/recovery became stronger. The older planned engine scored 12/12 at 8.99 seconds median on the same seed. Across five seeds of these 12 families, the final engine passed **60/60**; seed 88014 was first-use for the pre-review candidate (also 12/12), but all release batches are reruns after the four review fixes. These are repeated development-set results, not a held-out score. The additional 20 families improved from 13/20 in the first expanded probe to **17/20**. Those probes informed development and are not held-out generalization scores.

Remaining failures: `number-checkboxes` (visual pattern), `form-sequence` (slider), and `form-sequence-3` (custom dropdown). They remain in the denominator and raw results. Final p95 uses the nearest-rank percentile over every case, including failures. These small samples and ordinary provider latency variation do not establish statistical superiority or SOTA.

The final headless JFK–SFO November 12–16, 2026 check passed all eight independent checks in **15.18 seconds** of task-loop time, using 12 actions, 2 text calls and 3 recovery hints. It excludes initial Chrome startup/navigation and host verification. The earlier fast loop's two successful examples were 8.74/8.20 seconds; this stronger configuration trades some speed for recovery and completion checking. The final screenshot and encoded dates in the URL were reviewed; nothing was booked. All three flight runs in this iteration passed; the last used the released implementation.

Validation: **826 unit tests passed**, 3 skipped, 1 expected failure; Ruff, portable skill/plugin validators, headless control fixtures, explicit no-submit fixture, and fresh wheel import/resources/CLI checks passed. These are local checks, not GitHub Actions or native desktop acceptance.

## Experiment record

There were **429 recorded MiniWoB++ case executions** in this iteration, including unsuccessful candidates and focused reruns. The loop stopped after the requested 12/12 target, repeat checks, first-use seed, broader-scope probe and post-review acceptance were complete. The first recorded run began at 16:43 UTC and the final new-seed batch began at 17:09 UTC. Review fixes and final acceptance followed through 17:22 UTC, then packaging. User authorization covered the low-cost API tests and headless execution. Provider-reported text/recovery charges total about **$0.092**; this excludes Jev, failed calls without usage, flight checks, and Codex itself, so it is not a total bill.

[All case results, candidate source hashes and aggregate metrics](../bench/published/2026-10-01-reliability/summary.json) are published. Exact final engine hashes were checked against every final batch. Several discarded configurations briefly achieved 12/12 before fresh seeds exposed regressions; they are retained, rather than treating an early perfect result as sufficient. The final source is the combined retained candidate, not a cherry-picked union of passing cases.

| Candidate change | Observation | Decision |
|---|---|---|
| Context, current control state and field freshness | 11/12; form completion still premature | Keep observations, add completion audit |
| Completion audit alone | Fixed form; intermittent pagination/provider failures remained | Keep audit, investigate fresh cases |
| Recovery using the text writer model | 12/12 once, then 22/24 on fresh seeds | Replace recovery model; keep failures |
| Small dedicated recovery model and request cancellation | 12/12, but 21/24; expanded set 13/20 | Keep deadline, improve observed controls and positions |
| Richer groups, panel links, paragraphs and autocomplete | Expanded set 16/20; wrong pagination hints persisted | Keep control fixes, reject hints contradicted by observed ordinal facts |
| Final constraint and control checks | 60/60 core, 17/20 broader; real flight and no-submit pass | Retain; defer unsupported visual/slider/custom-dropdown work |

Reproduce with `bench/run_miniwob.py --mode ultrafast` and the frozen splits `fast_comparison`, `fast_reliability`, `fast_transfer`, `fast_prospective`, or `fast_holdout`; supply the pinned checkout and an output directory. The first-use label describes this experiment's chronology, not a property preserved after rerunning that seed. Some broader and final-seed checks overlapped a separate headless flight check; timing is local observational evidence, not a controlled interleaved speed trial.

## Evidence and limitations

Results and measured code hashes are published with this report. Earlier failures remain part of the experiment log. Local unit and integration checks cover request cancellation, provider isolation, missing source context, completion auditing, nested scrolling, stale fields, hidden radio labels and draft preservation.

The browser loop still cannot reliably solve visual puzzles, arbitrary canvas operations, dragging, sliders, iframes or new tabs. The older planned engine remains available explicitly for broader visual/control support. Native Mac behavior is unchanged and was not retested in this iteration. No comparison against Codex computer use or OSWorld evaluation was performed.

## Final review

Independent Spec, Security and Standards agents reviewed the working changes against base `d56ef1c`. Four distinct P2 findings were fixed before release: completion auditing had omitted checked/selected state; field freshness did not cover external text sources; `aria-current="false"` was treated as active; and optional recovery failure could abort an otherwise usable click-only run. Completion criteria now preserve control state, fills revalidate their writer evidence, inactive pagination markers are excluded, and terminal choices bypass recovery while unavailable/null guidance preserves the validated Jev choice. A focused Spec follow-up found no unresolved issue in completion/source validation.

Regression checks cover these failures, including a real headless fixture that rejects a changed external invoice reference while tolerating an unrelated countdown. The no-submit fixture still passed after the fixes. All benchmark results are retained; release acceptance reran the five batches against the reviewed implementation rather than attributing older measurements to changed code. GitHub Actions was not run; native desktop and unsupported visual controls remain outside this acceptance.
