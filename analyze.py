"""A simple program form comparing the time-in-market versus cost-averaging
investment strategies.

Example usage:

  python analyze.py data/sp500.csv \
    --dollars-to-invest=100000 \
    --weeks-to-hold=1000 \
    --num-buys=52 \
    --days-between-buys=10

"""
import argparse
import collections
import csv
import datetime
import sys


# The number of buckets to compute for percentiles.
NUM_BUCKETS = 10


Day = collections.namedtuple('Day', ['date', 'close'])


def parse_data(file_path):
    result = []

    with open(file_path) as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        date_idx = header.index('Date')
        close_idx = header.index('Adj Close')

        for row in reader:
            result.append(Day(
                date=datetime.date.fromisoformat(row[date_idx]),
                close=float(row[close_idx])))

    return result


def find(data, target):
    for i, day in enumerate(data):
        if day.date >= target:
            return i
    return None


def calculate_gains(
        data, dollars_to_invest, num_buys, days_between_buys,
        hold_weeks):
    gains = []
    start = 0
    end = find(data, data[0].date + hold_weeks)

    while end < len(data):
        num_shares = 0
        for i in range(num_buys):
            num_shares += (dollars_to_invest /
                           num_buys /
                           data[start + i * days_between_buys].close)
        gains.append(num_shares * data[end].close - dollars_to_invest)
        start += 1
        end += 1

    return gains


def compute_statistics(gains):
    gains = sorted(gains)
    buckets = []
    for i in range(NUM_BUCKETS):
        buckets.append(gains[int(i * 1.0 / NUM_BUCKETS * len(gains))])
    buckets.append(gains[-1])
    return [int(bucket) for bucket in buckets]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('--dollars-to-invest', type=int, default=100000)
    parser.add_argument('--weeks-to-hold', type=int, default=52 * 10)
    parser.add_argument('--num-buys', type=int, default=30)
    parser.add_argument('--days-between-buys', type=int, default=5)
    args = parser.parse_args()

    data = parse_data(args.data)
    time_in_market_gains = calculate_gains(
        data,
        num_buys=1,
        days_between_buys=1,
        dollars_to_invest=args.dollars_to_invest,
        hold_weeks=datetime.timedelta(weeks=args.weeks_to_hold))
    cost_averaging_gains = calculate_gains(
        data,
        num_buys=args.num_buys,
        days_between_buys=args.days_between_buys,
        dollars_to_invest=args.dollars_to_invest,
        hold_weeks=datetime.timedelta(weeks=args.weeks_to_hold))

    print('time in market', compute_statistics(time_in_market_gains))
    print('cost averaging', compute_statistics(cost_averaging_gains))
