import json
from pathlib import Path
import tempfile
import unittest

from looplab.checks import verify
from looplab.engine import load_spec, review_run, run_loop

SPEC = Path(__file__).resolve().parents[1] / 'examples/workshop-booking.json'


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'run'

    def test_failed_draft_is_repaired_but_not_auto_delivered(self):
        run = run_loop(SPEC, self.output)
        self.assertEqual(run['status'], 'awaiting_review')
        self.assertEqual(len(run['attempts']), 2)
        cases = run['attempts'][0]['gates'][-1]['cases']
        self.assertEqual({c['id'] for c in cases if not c['passed']},
                         {'positive_request', 'nonnegative_booked'})
        self.assertTrue(all(g['passed'] for g in run['attempts'][-1]['gates']))
        self.assertFalse((self.output / 'delivery').exists())
        stages = [e['stage'] for e in run['events']]
        self.assertEqual(stages, ['observe', 'plan', 'generate', 'verify', 'reflect',
                                  'generate', 'verify', 'review_requested'])

    def test_approval_delivers_verified_source(self):
        run_loop(SPEC, self.output)
        run = review_run(self.output, 'approve')
        self.assertEqual(run['status'], 'delivered')
        source = (self.output / 'delivery/booking_policy.py').read_text()
        self.assertEqual(source, run['attempts'][-1]['source'])
        self.assertIn('delivered', (self.output / 'report.html').read_text())

    def test_rejection_does_not_deliver(self):
        run_loop(SPEC, self.output)
        self.assertEqual(review_run(self.output, 'reject')['status'], 'rejected')
        self.assertFalse((self.output / 'delivery').exists())
        with self.assertRaises(ValueError):
            review_run(self.output, 'approve')

    def test_iteration_limit_is_a_stop_not_success(self):
        run = run_loop(SPEC, self.output, max_iterations=1)
        self.assertEqual(run['status'], 'iteration_limit')
        with self.assertRaises(ValueError):
            review_run(self.output, 'approve')

    def test_legacy_requires_human_context(self):
        run = run_loop(SPEC, self.output, mode='legacy')
        self.assertEqual(run['status'], 'needs_human_context')
        self.assertEqual(run['attempts'], [])
        with self.assertRaises(ValueError):
            review_run(self.output, 'approve')

    def test_legacy_context_is_visible_in_trace(self):
        run = run_loop(SPEC, self.output, mode='legacy', context='Keep the public function contract.')
        self.assertEqual(run['status'], 'awaiting_review')
        self.assertEqual(run['events'][1]['stage'], 'human_context')

    def test_artifact_change_blocks_approval(self):
        run_loop(SPEC, self.output)
        (self.output / 'attempt_02.py').write_text('def can_book(capacity, booked, requested): return True')
        with self.assertRaisesRegex(ValueError, 'changed'):
            review_run(self.output, 'approve')
        self.assertFalse((self.output / 'delivery').exists())

    def test_spec_change_blocks_approval(self):
        run_loop(SPEC, self.output)
        (self.output / 'spec.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'changed'):
            review_run(self.output, 'approve')

    def test_existing_run_is_preserved(self):
        run_loop(SPEC, self.output)
        original = (self.output / 'run.json').read_bytes()
        with self.assertRaises(ValueError):
            run_loop(SPEC, self.output)
        self.assertEqual((self.output / 'run.json').read_bytes(), original)

    def test_invalid_budget_and_empty_acceptance_rejected(self):
        with self.assertRaises(ValueError):
            run_loop(SPEC, self.output, max_iterations=0)
        empty = Path(self.temp.name) / 'empty.json'
        empty.write_text(json.dumps({'id': 'empty', 'acceptance': []}))
        with self.assertRaises(ValueError):
            run_loop(empty, self.output)
        self.assertFalse(self.output.exists())

    def test_duplicate_case_ids_rejected(self):
        spec = load_spec(SPEC)
        spec['acceptance'][1]['id'] = spec['acceptance'][0]['id']
        duplicate = Path(self.temp.name) / 'duplicate.json'
        duplicate.write_text(json.dumps(spec))
        with self.assertRaisesRegex(ValueError, 'unique'):
            load_spec(duplicate)

    def test_unpermitted_source_is_not_executed(self):
        spec = load_spec(SPEC)
        for source in ['import os', 'def can_book(capacity, booked, requested): return print(1)',
                       'def can_book(capacity, booked, requested): return capacity.real']:
            with self.subTest(source=source):
                gates = verify(source, spec)
                self.assertEqual(gates[-1], {'gate': 'restricted_syntax', 'passed': False})
        self.assertEqual(verify('def broken(:', spec)[0]['passed'], False)


if __name__ == '__main__':
    unittest.main()
