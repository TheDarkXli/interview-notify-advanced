#!/usr/bin/env python3

"""
View interview statistics from the analytics database
"""

import argparse
from pathlib import Path
from datetime import datetime
from interview_database import InterviewDatabase


def format_timestamp(ts_str):
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts_str


def print_statistics(db_path=None, days=30, channel=None):
    """Print interview statistics"""
    db = InterviewDatabase(db_path)

    print("=" * 70)
    print(f"Interview Statistics (Last {days} days)")
    print("=" * 70)
    print()

    stats = db.get_statistics(days=days, channel=channel)

    print(f"📊 Total Interviews:     {stats['total_interviews']}")
    print(f"✅ Passed:               {stats['passed']} ({stats['pass_rate']}%)")
    print(f"❌ Failed:               {stats['failed']}")
    print(f"⏰ Missed:               {stats['missed']}")
    print(f"📈 Average Queue Length: {stats['avg_queue_length']}")
    print()

    if stats['busiest_hours']:
        print("🕐 Busiest Hours (most interviews):")
        for hour, count in stats['busiest_hours']:
            print(f"   {hour:02d}:00 - {count} interviews")
        print()

    print("-" * 70)
    print("Recent Interviews:")
    print("-" * 70)

    recent = db.get_recent_interviews(limit=15, channel=channel)
    if recent:
        for event in recent:
            timestamp = format_timestamp(event['timestamp'])
            username = event['username']
            event_type = event['event_type']

            if event_type == 'started':
                queue = event.get('queue_length', '?')
                print(f"[{timestamp}] {username:20s} → Started (queue: {queue})")
            elif event_type in ['passed', 'failed', 'missed']:
                emoji = {'passed': '✅', 'failed': '❌', 'missed': '⏰'}[event_type]
                print(f"[{timestamp}] {username:20s} → {emoji} {event_type.upper()}")
    else:
        print("No recent interviews found")

    print()
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='View interview statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--db',
        type=Path,
        help='Path to analytics database (default: ~/.interview-notify-history.db)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to show statistics for (default: 30)'
    )
    parser.add_argument(
        '--channel',
        type=str,
        help='Filter by specific channel (optional)'
    )

    args = parser.parse_args()

    try:
        print_statistics(args.db, args.days, args.channel)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
