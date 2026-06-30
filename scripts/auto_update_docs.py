"""Auto-update logbook and fortnight report with simple, human-readable entries.

Usage examples:
  python scripts/auto_update_docs.py --action export_labeling --summary "Exported labeling candidates" --files outputs/labeling_candidates.csv outputs/review_summary_confidence.csv

This appends a short entry to `logs/daily_logbook.md` and `docs/fortnight_report_3.md` including date, brief summary, and file references.
"""
from pathlib import Path
import argparse
from datetime import datetime
import textwrap


ROOT = Path.cwd()
LOGBOOK = ROOT / 'logs' / 'daily_logbook.md'
FORTNIGHT = ROOT / 'docs' / 'fortnight_report_3.md'


def append_logbook(entry_lines):
    header = f"### Date: {datetime.utcnow().date().isoformat()}"
    content = '\n'.join(['* ' + l for l in entry_lines])
    with open(LOGBOOK, 'a', encoding='utf-8') as fh:
        fh.write('\n' + header + '\n' + content + '\n')


def append_fortnight(entry_title, entry_body):
    sep = '\n'
    block = f"\n### {entry_title}\n\n{entry_body}\n"
    with open(FORTNIGHT, 'a', encoding='utf-8') as fh:
        fh.write(block)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--action', required=True, help='Short action id')
    p.add_argument('--summary', required=True, help='One-line summary')
    p.add_argument('--files', nargs='*', help='Related files')
    p.add_argument('--notes', help='Optional longer notes')
    args = p.parse_args()

    date = datetime.utcnow().strftime('%Y-%m-%d')
    entry_lines = []
    entry_lines.append(f"**Action:** {args.action}")
    entry_lines.append(f"**Summary:** {args.summary}")
    if args.files:
        for f in args.files:
            entry_lines.append(f"**File:** {f}")
    if args.notes:
        wrapped = textwrap.fill(args.notes, width=80)
        entry_lines.append(f"**Notes:** {wrapped}")

    # Append to daily logbook
    append_logbook(entry_lines)

    # Append a concise entry to fortnight report
    title = f"Verification: {args.summary} ({date})"
    body_lines = [f"- Files: {', '.join(args.files) if args.files else 'none'}"]
    if args.notes:
        body_lines.append('\n' + args.notes)
    body = '\n'.join(body_lines)
    append_fortnight(title, body)

    print('Updated logbook and fortnight report')


if __name__ == '__main__':
    main()
