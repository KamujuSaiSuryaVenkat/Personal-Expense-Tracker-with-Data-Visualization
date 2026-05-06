"""Generate a synthetic large expenses CSV for testing uploads.
Usage: python scripts/generate_large_csv.py --rows 100000 --output data/large_sample_expenses.csv
"""
import csv
import random
from datetime import datetime, timedelta
import argparse

def random_date(start, end):
    delta = end - start
    rand_days = random.randint(0, delta.days)
    return start + timedelta(days=rand_days)

DESCRIPTIONS = [
    'Grocery', 'Restaurant', 'Taxi', 'Bus', 'Flight Ticket', 'Subscription', 'Gym Membership',
    'Electricity Bill', 'Internet Bill', 'Hotel', 'Movie', 'Book Purchase', 'Pharmacy', 'Coffee',
    'Lunch', 'Dinner', 'Online Shopping', 'Course Purchase', 'Tuition Fee', 'Insurance', 'Fuel', 'Parking'
]
PAYMENT_METHODS = ['Card', 'Cash', 'UPI', 'Transfer']
CATEGORIES = ['Food & Dining', 'Transportation', 'Utilities', 'Health & Medical', 'Entertainment', 'Shopping', 'Education', 'Other']

parser = argparse.ArgumentParser()
parser.add_argument('--rows', type=int, default=100000, help='Number of rows to generate')
parser.add_argument('--output', type=str, default='data/large_sample_expenses.csv', help='Output CSV path')
args = parser.parse_args()

rows = args.rows
output = args.output

start_date = datetime(2019,1,1)
end_date = datetime(2024,12,31)

with open(output, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Description','Amount','PaymentMethod','Category'])
    for i in range(rows):
        d = random_date(start_date, end_date).strftime('%Y-%m-%d')
        desc = random.choice(DESCRIPTIONS)
        # Amount distribution: many small amounts, some large
        if random.random() < 0.92:
            amt = round(random.uniform(10, 2000), 2)
        else:
            amt = round(random.uniform(2000, 15000), 2)
        pm = random.choice(PAYMENT_METHODS)
        # category correlated with description
        if desc in ('Grocery','Lunch','Dinner','Coffee','Restaurant'):
            cat = 'Food & Dining'
        elif desc in ('Taxi','Bus','Fuel','Parking','Flight Ticket'):
            cat = 'Transportation'
        elif desc in ('Electricity Bill','Internet Bill'):
            cat = 'Utilities'
        elif desc in ('Pharmacy','Health Insurance'):
            cat = 'Health & Medical'
        elif desc in ('Subscription','Movie','Book Purchase'):
            cat = 'Entertainment'
        elif desc in ('Online Shopping','Hotel'):
            cat = 'Shopping'
        elif desc in ('Course Purchase','Tuition Fee'):
            cat = 'Education'
        else:
            cat = random.choice(CATEGORIES)
        writer.writerow([d, desc, amt, pm, cat])

print(f"Generated {rows} rows -> {output}")
