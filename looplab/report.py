"""A standalone HTML walkthrough of a real local run."""
import html
import json


def write_report(directory, run):
    esc = html.escape
    rows = []
    for event in run['events']:
        details = {k: v for k, v in event.items() if k not in {'step', 'stage'}}
        rows.append(f'<article><span>{event["step"]:02}</span><div><h3>{esc(event["stage"])}</h3>'
                    f'<pre>{esc(json.dumps(details, ensure_ascii=False, indent=2))}</pre></div></article>')
    attempts = []
    for attempt in run['attempts']:
        results = ''.join(f'<li>{esc(g["gate"])}: {"PASS" if g["passed"] else "FAIL"}</li>' for g in attempt['gates'])
        attempts.append(f'<section><h3>Attempt {attempt["number"]}</h3><ul>{results}</ul>'
                        f'<pre>{esc(attempt["source"])}</pre></section>')
    document = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Spec to Delivery · Run Report</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f5f9;color:#17263d;font:16px/1.6 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:48px 24px}header{background:#15283f;color:white;padding:36px;border-radius:20px}h1{font-size:36px;line-height:1.2;margin:12px 0}h2{margin-top:36px}h3{margin:0 0 12px}small{color:#b7d5f0}.status{display:inline-block;padding:6px 14px;border-radius:30px;background:#e2f7f0;color:#164d3b;font-weight:650}section,article{background:white;border:1px solid #dce4ef;border-radius:14px;padding:22px;margin:14px 0}article{display:flex;gap:20px}article span{color:#4775ba;font-size:22px;font-weight:700}article div{min-width:0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 ui-monospace,monospace}nav{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}nav a{color:#285e94}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:28px}main{padding:20px 12px}header{padding:24px}}
</style><main><header><small>SPECIFICATION → FEEDBACK → REVIEW → DELIVERY</small><h1>Spec to Delivery Loop</h1>
<p>A fictional workshop-booking policy, with real Python checks and a visible repair cycle.</p>
<div class="status">STATUS</div><p>MODE · Scripted adapter · No API key</p></header>
<nav><a href="#attempts">Compare attempts</a><a href="#trace">Inspect execution trace</a></nav>
<h2 id="attempts">Artifacts and quality gates</h2><div class="grid">ATTEMPTS</div>
<h2 id="trace">Execution trace</h2>EVENTS
<footer><p>The adapter is deterministic; the checks execute locally. Passing checks still requires a separate review decision. This report is a portfolio demonstration, not evidence of an enterprise deployment.</p></footer></main></html>'''
    document = document.replace('STATUS', esc(run['status'])).replace('MODE', esc(run['mode']))
    document = document.replace('ATTEMPTS', ''.join(attempts)).replace('EVENTS', ''.join(rows))
    (directory / 'report.html').write_text(document, encoding='utf-8')
