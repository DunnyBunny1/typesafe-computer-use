"""Headless, local-only control integration check; no model calls."""

import tempfile
from pathlib import Path

from typesafe_computer_use._vendor.jev_ultrafast.browser import Browser
from typesafe_computer_use.browser import act
from typesafe_computer_use.browser.cdp import Chrome

with tempfile.TemporaryDirectory() as tmp:
    fixture = Path(tmp) / "controls.html"
    fixture.write_text("""<!doctype html><html><body>
<style>input[type=radio]{display:none} .custom{cursor:pointer}</style>
<input id="nonstop" type="radio"><label for="nonstop">Direct service</label>
<input id="query" aria-label="Search" autofocus>
<span class="custom" onclick="document.body.dataset.clicked='yes'">Custom link</span>
</body></html>""")
    with Chrome() as chrome, chrome.attach() as session:
        act.navigate(session, fixture.as_uri())
        act.wait_for_load(session)
        browser = Browser(session)
        page = browser.observe(screenshot=False)
        label = next(a for a in page["actions"] if a["label"] == "Direct service")
        assert label["role"] == "radio" and label["checked"] == "false"
        assert not any(a["label"] == "Open Search" for a in page["actions"])
        browser.act(label, page)
        page = browser.observe(screenshot=False)
        assert next(a for a in page["actions"] if a["label"] == "Direct service")["checked"] == "true"
        custom = next(a for a in page["actions"] if a["label"] == "Custom link")
        browser.act(custom, page)
        assert session.evaluate("document.body.dataset.clicked") == "yes"
print("PASS: hidden radio labels, checked state, focused field, custom pointer control and real mouse input")
