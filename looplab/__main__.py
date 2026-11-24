import argparse
from pathlib import Path

from .engine import review_run, run_loop


def main():
    parser = argparse.ArgumentParser(description='Inspect a specification-driven development loop with synthetic data.')
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('run', help='Generate, check, reflect and request review')
    run.add_argument('--spec', default='examples/workshop-booking.json')
    run.add_argument('--output', default='runs/demo')
    run.add_argument('--mode', choices=['isolated', 'legacy'], default='isolated')
    run.add_argument('--context', type=Path, help='Human-written compatibility notes for the legacy route')
    run.add_argument('--max-iterations', type=int, default=3)
    review = sub.add_parser('review', help='Record an explicit local approval or rejection')
    review.add_argument('output')
    review.add_argument('--decision', choices=['approve', 'reject'], required=True)
    args = parser.parse_args()
    try:
        if args.command == 'run':
            result = run_loop(args.spec, args.output, mode=args.mode,
                              context=args.context.read_text(encoding='utf-8') if args.context else None,
                              max_iterations=args.max_iterations)
        else:
            result = review_run(args.output, args.decision)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'Error: {exc}' + chr(10))
    print(f'Status: {result["status"]}; attempts: {len(result["attempts"])}')
    print(f'Report: {Path(args.output) / "report.html"}')
    if result['status'] == 'iteration_limit':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
