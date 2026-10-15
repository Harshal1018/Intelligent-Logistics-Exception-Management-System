import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data' / 'generated'
DATA_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

hubs = [
    ('HUB001', 'North DC', 'Delhi', 'Delhi', 'North', 'Medium', 20000),
    ('HUB002', 'West Gateway', 'Mumbai', 'Maharashtra', 'West', 'High', 22000),
    ('HUB003', 'Central Hub', 'Bengaluru', 'Karnataka', 'South', 'Medium', 19000),
    ('HUB004', 'East Sort Center', 'Kolkata', 'West Bengal', 'East', 'Low', 18000),
    ('HUB005', 'Hyderabad Hub', 'Hyderabad', 'Telangana', 'South', 'High', 21000),
    ('HUB006', 'Pune Regional', 'Pune', 'Maharashtra', 'West', 'Medium', 17000),
    ('HUB007', 'Ahmedabad Depot', 'Ahmedabad', 'Gujarat', 'West', 'Low', 16000),
    ('HUB008', 'Chennai Terminal', 'Chennai', 'Tamil Nadu', 'South', 'High', 20000),
    ('HUB009', 'Jaipur Link', 'Jaipur', 'Rajasthan', 'North', 'Medium', 16000),
    ('HUB010', 'Lucknow Relay', 'Lucknow', 'Uttar Pradesh', 'North', 'Medium', 15000),
    ('HUB011', 'Patna Center', 'Patna', 'Bihar', 'East', 'High', 14000),
    ('HUB012', 'Nagpur Node', 'Nagpur', 'Maharashtra', 'Central', 'Low', 15000),
    ('HUB013', 'Coimbatore Sort', 'Coimbatore', 'Tamil Nadu', 'South', 'Medium', 13000),
    ('HUB014', 'Bhopal Line', 'Bhopal', 'Madhya Pradesh', 'Central', 'Low', 14000),
    ('HUB015', 'Gurugram Connect', 'Gurugram', 'Haryana', 'North', 'High', 18000),
]

carrier_profiles = [
    ('CAR001', 'SpeedLine', 'Express', 0.94, 6.5, 1400),
    ('CAR002', 'RapidFreight', 'Ground', 0.9, 8.2, 1800),
    ('CAR003', 'MetroCargo', 'Regional', 0.88, 10.1, 1200),
    ('CAR004', 'PrimeTransit', 'Express', 0.92, 7.3, 1500),
    ('CAR005', 'BlueRoute', 'Ground', 0.84, 12.5, 2200),
    ('CAR006', 'NationalLink', 'Regional', 0.86, 11.0, 1600),
    ('CAR007', 'AirSwift', 'Air', 0.96, 5.4, 900),
    ('CAR008', 'SafeMove', 'Ground', 0.89, 9.0, 2000),
]

customer_types = ['Retail', 'SMB', 'Enterprise']
shipment_types = ['Standard', 'Express', 'Cold Chain', 'Fragile', 'Bulk']
priority_levels = ['Normal', 'Priority', 'VIP']
exception_reasons = [
    'Hub Congestion',
    'Weather Delay',
    'Incorrect Address',
    'Failed Delivery Attempt',
    'Vehicle Breakdown',
    'Sorting Delay',
    'Customs Clearance',
    'Road Closure',
    'Packaging Issue',
    'Customer Unavailable',
]

hub_df = pd.DataFrame(hubs, columns=['hub_id', 'hub_name', 'city', 'state', 'region', 'congestion_level', 'capacity_kgs'])
hub_df['created_at'] = pd.Timestamp('2024-01-01')

carrier_df = pd.DataFrame(carrier_profiles, columns=['carrier_id', 'carrier_name', 'carrier_type', 'on_time_rate', 'avg_delay_hours', 'fleet_size'])
carrier_df['created_at'] = pd.Timestamp('2024-01-01')
carrier_lookup = {profile[0]: profile for profile in carrier_profiles}
carrier_ids = list(carrier_lookup.keys())
carrier_probabilities = np.array([0.14, 0.16, 0.14, 0.15, 0.12, 0.14, 0.08, 0.07])

rng = np.random.default_rng(123)
customer_rows = []
for i in range(1, 12001):
    city = ['Delhi', 'Mumbai', 'Bengaluru', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Chennai', 'Jaipur', 'Lucknow', 'Patna', 'Nagpur', 'Coimbatore', 'Bhopal', 'Gurugram'][i % 15]
    state_map = {
        'Delhi': 'Delhi',
        'Mumbai': 'Maharashtra', 'Bengaluru': 'Karnataka', 'Kolkata': 'West Bengal',
        'Hyderabad': 'Telangana', 'Pune': 'Maharashtra', 'Ahmedabad': 'Gujarat',
        'Chennai': 'Tamil Nadu', 'Jaipur': 'Rajasthan', 'Lucknow': 'Uttar Pradesh',
        'Patna': 'Bihar', 'Nagpur': 'Maharashtra', 'Coimbatore': 'Tamil Nadu',
        'Bhopal': 'Madhya Pradesh', 'Gurugram': 'Haryana'
    }
    customer_rows.append({
        'customer_id': i,
        'customer_name': f'Customer_{i}',
        'customer_type': customer_types[i % 3],
        'city': city,
        'state': state_map[city],
        'created_at': pd.Timestamp('2024-01-01') + pd.Timedelta(days=i % 365)
    })
customers_df = pd.DataFrame(customer_rows)

hub_list = hub_df['hub_id'].tolist()
route_distance = {}
for origin in hub_list:
    for destination in hub_list:
        if origin == destination:
            distance = 120
        else:
            origin_idx = hub_list.index(origin)
            destination_idx = hub_list.index(destination)
            distance = 220 + abs(origin_idx - destination_idx) * 120 + (origin_idx % 3) * 45 + (destination_idx % 2) * 60
        route_distance[(origin, destination)] = distance

shipment_rows = []
status_history_rows = []
exception_rows = []
hub_probabilities = np.array([0.12, 0.10, 0.08, 0.07, 0.09, 0.06, 0.05, 0.09, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.06])
for shipment_no in range(1, 100001):
    customer_id = int(rng.integers(1, 12001))
    origin_hub = np.random.choice(hub_list, p=hub_probabilities)
    destination_hub = np.random.choice(hub_list)
    if origin_hub == destination_hub:
        destination_hub = hub_list[(hub_list.index(origin_hub) + 1) % len(hub_list)]

    carrier_id = np.random.choice(carrier_ids, p=carrier_probabilities)
    _, _, carrier_type, on_time_rate, avg_delay_hours, fleet_size = carrier_lookup[carrier_id]

    origin_congestion = hub_df.loc[hub_df['hub_id'] == origin_hub, 'congestion_level'].iloc[0]
    destination_congestion = hub_df.loc[hub_df['hub_id'] == destination_hub, 'congestion_level'].iloc[0]
    congestion_factor = {'Low': 0.82, 'Medium': 1.0, 'High': 1.18}[origin_congestion] * {'Low': 0.8, 'Medium': 1.0, 'High': 1.2}[destination_congestion]

    distance_km = route_distance[(origin_hub, destination_hub)]
    shipment_type = np.random.choice(shipment_types, p=np.array([0.42, 0.25, 0.12, 0.08, 0.13]))
    priority = np.random.choice(priority_levels, p=np.array([0.7, 0.22, 0.08]))
    weight_kg = max(1.5, float(np.random.lognormal(mean=2.8, sigma=0.7)))

    month = int(np.random.choice(np.arange(1, 13), p=[0.06, 0.08, 0.09, 0.09, 0.08, 0.08, 0.08, 0.09, 0.09, 0.08, 0.09, 0.09]))
    season_multiplier = {1: 1.18, 2: 1.12, 3: 1.08, 4: 1.02, 5: 1.0, 6: 1.05, 7: 1.08, 8: 1.09, 9: 1.07, 10: 1.12, 11: 1.15, 12: 1.2}[month]

    base_prob = 0.12 + (distance_km / 4000) * 0.25 + (weight_kg / 45) * 0.08 + {'Normal': 0.0, 'Priority': 0.05, 'VIP': 0.12}[priority]
    base_prob += (1.0 - on_time_rate) * 0.17
    base_prob += (1.0 - (0.9 if origin_congestion == 'Low' else 0.8 if origin_congestion == 'Medium' else 0.7)) * 0.15
    base_prob += (1.0 - 0.85 if shipment_type == 'Cold Chain' else 0.0) * 0.05
    base_prob += (congestion_factor - 1) * 0.18
    base_prob += (season_multiplier - 1) * 0.12
    base_prob = min(0.82, max(0.03, base_prob))

    delay_flag = int(rng.random() < base_prob)
    shipment_date = pd.Timestamp('2024-01-01') + pd.Timedelta(days=int(rng.integers(0, 365)))
    planned_hours = max(18, int(distance_km / 12) + {'Standard': 18, 'Express': 10, 'Cold Chain': 24, 'Fragile': 20, 'Bulk': 30}[shipment_type])
    if priority == 'VIP':
        planned_hours *= 0.82
    elif priority == 'Priority':
        planned_hours *= 0.9

    if delay_flag:
        actual_hours = int(planned_hours * (1 + rng.uniform(0.28, 0.95)))
        if shipment_type == 'Cold Chain':
            actual_hours += int(rng.uniform(6, 18))
        if origin_congestion == 'High' or destination_congestion == 'High':
            actual_hours += int(rng.uniform(8, 20))
    else:
        actual_hours = int(planned_hours * (1 + rng.uniform(0.02, 0.18)))

    sla_hours = max(24, int(planned_hours * {'Standard': 1.15, 'Express': 1.25, 'Cold Chain': 1.35, 'Fragile': 1.3, 'Bulk': 1.4}[shipment_type]))
    if priority == 'VIP':
        sla_hours = max(18, int(sla_hours * 0.8))
    if actual_hours > sla_hours:
        sla_breach = 1
    else:
        sla_breach = 0

    status = 'Delayed' if delay_flag else 'Delivered'
    shipment_id = f'SHP{shipment_no:06d}'
    planned_dt = pd.Timestamp(shipment_date) + pd.Timedelta(hours=6)
    actual_dt = planned_dt + pd.Timedelta(hours=actual_hours)

    shipment_rows.append({
        'shipment_id': shipment_id,
        'customer_id': customer_id,
        'carrier_id': carrier_id,
        'origin_hub_id': origin_hub,
        'destination_hub_id': destination_hub,
        'shipment_type': shipment_type,
        'priority': priority,
        'weight_kg': round(weight_kg, 2),
        'distance_km': int(distance_km),
        'sla_hours': int(sla_hours),
        'planned_delivery_datetime': planned_dt,
        'actual_delivery_datetime': actual_dt,
        'status': status,
        'delay_flag': delay_flag,
        'sla_breach': sla_breach,
        'created_at': pd.Timestamp.now().normalize() - pd.Timedelta(days=shipment_no % 180),
    })

    history_steps = [
        ('Created', planned_dt - pd.Timedelta(days=2)),
        ('In Transit', planned_dt - pd.Timedelta(hours=max(10, int(actual_hours * 0.6)))),
        ('At Hub', planned_dt - pd.Timedelta(hours=max(4, int(actual_hours * 0.3)))),
        ('Delivered', actual_dt) if not delay_flag else ('Delayed', actual_dt),
    ]
    for status_name, tstamp in history_steps:
        status_history_rows.append({
            'shipment_id': shipment_id,
            'status': status_name,
            'status_timestamp': tstamp,
            'remarks': f'{status_name} event for shipment {shipment_id}'
        })

    if delay_flag:
        exception_count = int(np.random.choice([1, 2, 3], p=[0.7, 0.22, 0.08]))
        for _ in range(exception_count):
            reason = np.random.choice(exception_reasons, p=[0.2, 0.1, 0.12, 0.12, 0.12, 0.18, 0.05, 0.05, 0.03, 0.03])
            severity = np.random.choice(['Low', 'Medium', 'High', 'Critical'], p=[0.18, 0.38, 0.32, 0.12])
            exception_rows.append({
                'shipment_id': shipment_id,
                'exception_reason': reason,
                'exception_type': 'Operational Delay',
                'severity': severity,
                'status': 'Open' if np.random.rand() < 0.45 else 'Resolved',
                'created_at': actual_dt - pd.Timedelta(hours=np.random.randint(1, 36)),
                'resolved_at': actual_dt if np.random.rand() < 0.3 else pd.NaT,
                'assigned_to': f'Ops_{np.random.randint(1, 30)}',
                'notes': f'Issue recorded due to {reason.lower()}.'
            })
    elif np.random.rand() < 0.08:
        reason = np.random.choice(exception_reasons, p=[0.1, 0.05, 0.22, 0.12, 0.08, 0.16, 0.06, 0.06, 0.08, 0.07])
        exception_rows.append({
            'shipment_id': shipment_id,
            'exception_reason': reason,
            'exception_type': 'Operational Delay',
            'severity': 'Low',
            'status': 'Closed',
            'created_at': planned_dt - pd.Timedelta(hours=np.random.randint(1, 10)),
            'resolved_at': planned_dt - pd.Timedelta(hours=np.random.randint(0, 5)),
            'assigned_to': f'Ops_{np.random.randint(1, 30)}',
            'notes': f'Minor operational exception due to {reason.lower()}.'
        })

customers_df.to_csv(DATA_DIR / 'customers.csv', index=False)
hub_df.to_csv(DATA_DIR / 'hubs.csv', index=False)
carrier_df.to_csv(DATA_DIR / 'carriers.csv', index=False)
shipments_df = pd.DataFrame(shipment_rows)
shipments_df.to_csv(DATA_DIR / 'shipments.csv', index=False)
exceptions_df = pd.DataFrame(exception_rows)
exceptions_df.to_csv(DATA_DIR / 'exceptions.csv', index=False)
status_df = pd.DataFrame(status_history_rows)
status_df.to_csv(DATA_DIR / 'shipment_status_history.csv', index=False)

print(f'Generated {len(customers_df)} customers')
print(f'Generated {len(hub_df)} hubs')
print(f'Generated {len(carrier_df)} carriers')
print(f'Generated {len(shipments_df)} shipments')
print(f'Generated {len(exceptions_df)} exceptions')
print(f'Generated {len(status_df)} status history rows')
print(f'Sample delay rate: {shipments_df["delay_flag"].mean():.2%}')
