"""Bounded generation/check/reflection loop with an explicit delivery decision."""
import hashlib
import json
from pathlib import Path

from .checks import verify
from .demo_agent import DemoAgent
from .report import write_report


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def record(run, stage, **data):
    run['events'].append({'step': len(run['events']) + 1, 'stage': stage, **data})


def save(directory, run):
    (directory / 'run.json').write_text(json.dumps(run, indent=2) + chr(10), encoding='utf-8')
    (directory / 'trace.jsonl').write_text(''.join(json.dumps(e) + chr(10) for e in run['events']), encoding='utf-8')
    write_report(directory, run)


def load_spec(path):
    spec = json.loads(Path(path).read_text(encoding='utf-8'))
    cases = spec.get('acceptance', [])
    if not spec.get('id') or not isinstance(cases, list) or not cases:
        raise ValueError('A spec must have an id and nonempty acceptance cases.')
    ids = []
    for case in cases:
        if (not isinstance(case.get('id'), str) or not case['id']
                or len(case.get('args', [])) != 3
                or any(type(v) is not int for v in case['args'])
                or type(case.get('expected')) is not bool):
            raise ValueError('Each case needs an id, three integer args and a boolean expectation.')
        ids.append(case['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('Acceptance IDs must be unique.')
    return spec


def run_loop(spec_path, output, *, mode='isolated', context=None, max_iterations=3, agent=None):
    if not 1 <= max_iterations <= 10:
        raise ValueError('max_iterations must be between 1 and 10.')
    if mode not in {'isolated', 'legacy'}:
        raise ValueError('mode must be isolated or legacy.')
    spec = load_spec(spec_path)
    if context is not None and (not isinstance(context, str) or not context.strip()):
        raise ValueError('Human context must be nonempty text.')
    directory = Path(output)
    if directory.exists():
        raise ValueError('Choose a new output directory; existing runs are never overwritten.')
    directory.mkdir(parents=True)
    spec_text = json.dumps(spec, indent=2) + chr(10)
    (directory / 'spec.json').write_text(spec_text, encoding='utf-8')
    run = {'spec_id': spec['id'], 'spec_sha256': digest(spec_text), 'mode': mode,
           'status': 'running', 'max_iterations': max_iterations, 'attempts': [], 'events': []}
    record(run, 'observe', spec_id=spec['id'], criteria=[c['id'] for c in spec['acceptance']])
    if mode == 'legacy' and context is None:
        run['status'] = 'needs_human_context'
        record(run, 'human_context_required', reason='Document existing behavior and compatibility constraints before generation.')
        save(directory, run)
        return run
    if context is not None:
        record(run, 'human_context', context=context)
    record(run, 'plan', tasks=['implement booking policy', 'verify all acceptance criteria', 'request final review'])
    adapter = agent or DemoAgent()
    feedback = []
    for number in range(1, max_iterations + 1):
        source = adapter.generate(spec, feedback)
        artifact = f'attempt_{number:02}.py'
        (directory / artifact).write_text(source, encoding='utf-8')
        record(run, 'generate', iteration=number, artifact=artifact, sha256=digest(source))
        gates = verify(source, spec)
        attempt = {'number': number, 'artifact': artifact, 'source': source,
                   'sha256': digest(source), 'gates': gates}
        run['attempts'].append(attempt)
        record(run, 'verify', iteration=number, gates=gates)
        if all(g['passed'] for g in gates):
            run['status'] = 'awaiting_review'
            record(run, 'review_requested', artifact=artifact, sha256=digest(source))
            break
        reflection = adapter.reflect(gates)
        feedback.append(reflection)
        record(run, 'reflect', iteration=number, **reflection)
    else:
        run['status'] = 'iteration_limit'
        record(run, 'stopped', reason='Iteration budget exhausted; no deliverable approved.')
    save(directory, run)
    return run


def review_run(output, decision):
    if decision not in {'approve', 'reject'}:
        raise ValueError('Decision must be approve or reject.')
    directory = Path(output)
    run = json.loads((directory / 'run.json').read_text(encoding='utf-8'))
    if run['status'] != 'awaiting_review':
        raise ValueError('Only a run awaiting review can receive a decision.')
    if decision == 'reject':
        run['status'] = 'rejected'
        record(run, 'human_review', decision='reject')
        save(directory, run)
        return run
    attempt = run['attempts'][-1]
    artifact = attempt['artifact']
    if artifact != f'attempt_{attempt["number"]:02}.py':
        raise ValueError('Invalid artifact path in run manifest.')
    source = (directory / artifact).read_text(encoding='utf-8')
    spec_text = (directory / 'spec.json').read_text(encoding='utf-8')
    if digest(source) != attempt['sha256'] or digest(spec_text) != run['spec_sha256']:
        raise ValueError('Artifact or spec changed after verification. Start a new run.')
    gates = verify(source, load_spec(directory / 'spec.json'))
    if not all(g['passed'] for g in gates):
        raise ValueError('Approval requires all quality gates to pass again.')
    destination = directory / 'delivery'
    destination.mkdir(exist_ok=False)
    (destination / 'booking_policy.py').write_text(source, encoding='utf-8')
    record(run, 'human_review', decision='approve', sha256=digest(source))
    record(run, 'deliver', artifact='delivery/booking_policy.py', sha256=digest(source))
    run['status'] = 'delivered'
    save(directory, run)
    return run
