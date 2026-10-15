from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data' / 'generated'
REPORT_DIR = ROOT / 'data' / 'reports'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

shipments = pd.read_csv(DATA_DIR / 'shipments.csv')
exceptions = pd.read_csv(DATA_DIR / 'exceptions.csv')

missing_values = shipments.isna().sum()
duplicates = shipments.duplicated().sum()

shipments['planned_delivery_datetime'] = pd.to_datetime(shipments['planned_delivery_datetime'])
shipments['actual_delivery_datetime'] = pd.to_datetime(shipments['actual_delivery_datetime'])
shipments['delivery_hours'] = (shipments['actual_delivery_datetime'] - shipments['planned_delivery_datetime']).dt.total_seconds() / 3600

kpis = {
    'total_shipments': int(len(shipments)),
    'delayed_shipments': int(shipments['delay_flag'].sum()),
    'on_time_delivery_percent': round((1 - shipments['delay_flag'].mean()) * 100, 2),
    'sla_breach_percent': round(shipments['sla_breach'].mean() * 100, 2),
    'average_delivery_time_hours': round(shipments['delivery_hours'].mean(), 2),
    'open_exceptions': int(exceptions[exceptions['status'].isin(['Open', 'Assigned', 'In Progress'])].shape[0]),
    'missing_values': missing_values.to_dict(),
    'duplicate_rows': duplicates,
}

exception_summary = exceptions['exception_reason'].value_counts().reset_index()
exception_summary.columns = ['exception_reason', 'count']

hub_performance = shipments.groupby('origin_hub_id').agg(total_shipments=('shipment_id', 'count'), delay_rate=('delay_flag', 'mean')).sort_values('delay_rate', ascending=False)
carrier_performance = shipments.groupby('carrier_id').agg(total_shipments=('shipment_id', 'count'), delay_rate=('delay_flag', 'mean')).sort_values('delay_rate', ascending=False)

q1 = shipments['delivery_hours'].quantile(0.25)
q3 = shipments['delivery_hours'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
outlier_count = int(((shipments['delivery_hours'] < lower_bound) | (shipments['delivery_hours'] > upper_bound)).sum())

summary = {
    'kpis': kpis,
    'top_exception_reasons': exception_summary.head(10).to_dict(orient='records'),
    'hub_performance': hub_performance.head(10).to_dict(),
    'carrier_performance': carrier_performance.head(10).to_dict(),
    'outlier_deliveries': outlier_count,
}

REPORT_DIR.joinpath('analysis_summary.json').write_text(str(summary).replace("'", '"'))
exception_summary.to_csv(REPORT_DIR / 'exception_reasons.csv', index=False)
hub_performance.to_csv(REPORT_DIR / 'hub_performance.csv', index=False)
carrier_performance.to_csv(REPORT_DIR / 'carrier_performance.csv', index=False)

print('KPI Summary:')
for key, value in kpis.items():
    print(f'{key}: {value}')
print('\nTop exception reasons:')
print(exception_summary.head(10).to_string(index=False))
print(f'\nOutlier shipments detected: {outlier_count}')
