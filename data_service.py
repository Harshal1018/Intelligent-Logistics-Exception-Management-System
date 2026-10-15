from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data' / 'generated'


def _load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def get_dashboard_metrics() -> dict:
    shipments = _load_csv('shipments.csv')
    exceptions = _load_csv('exceptions.csv')
    if shipments.empty:
        return {
            'total_shipments': 0,
            'delayed_shipments': 0,
            'on_time_delivery_pct': 0,
            'sla_breach_pct': 0,
            'average_delivery_time_hours': 0,
            'open_exceptions': 0,
        }

    shipments['actual_delivery_datetime'] = pd.to_datetime(shipments['actual_delivery_datetime'])
    shipments['planned_delivery_datetime'] = pd.to_datetime(shipments['planned_delivery_datetime'])
    shipments['delivery_hours'] = (shipments['actual_delivery_datetime'] - shipments['planned_delivery_datetime']).dt.total_seconds() / 3600

    return {
        'total_shipments': int(len(shipments)),
        'delayed_shipments': int(shipments['delay_flag'].sum()),
        'on_time_delivery_pct': round((1 - shipments['delay_flag'].mean()) * 100, 2),
        'sla_breach_pct': round(shipments['sla_breach'].mean() * 100, 2),
        'average_delivery_time_hours': round(shipments['delivery_hours'].mean(), 2),
        'open_exceptions': int(exceptions[exceptions['status'].isin(['Open', 'Assigned', 'In Progress'])].shape[0]),
    }


def get_shipments(limit: int = 50) -> list[dict]:
    shipments = _load_csv('shipments.csv')
    if shipments.empty:
        return []
    return shipments.head(limit).to_dict(orient='records')


def get_shipment_by_id(shipment_id: str) -> dict | None:
    shipments = _load_csv('shipments.csv')
    if shipments.empty:
        return None
    row = shipments[shipments['shipment_id'] == shipment_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def search_shipments(query: str) -> list[dict]:
    shipments = _load_csv('shipments.csv')
    if shipments.empty:
        return []
    text = str(query).strip().lower()
    if not text:
        return shipments.head(20).to_dict(orient='records')
    filtered = shipments[
        shipments['shipment_id'].astype(str).str.lower().str.contains(text) |
        shipments['status'].astype(str).str.lower().str.contains(text) |
        shipments['carrier_id'].astype(str).str.lower().str.contains(text) |
        shipments['origin_hub_id'].astype(str).str.lower().str.contains(text)
    ]
    return filtered.head(20).to_dict(orient='records')


def get_exception_queue() -> list[dict]:
    exceptions = _load_csv('exceptions.csv')
    if exceptions.empty:
        return []
    return exceptions.head(25).to_dict(orient='records')


def get_exception_by_id(exception_id: int) -> dict | None:
    exceptions = _load_csv('exceptions.csv')
    if exceptions.empty:
        return None
    row = exceptions[exceptions.index == exception_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def get_risk_summary() -> list[dict]:
    shipments = _load_csv('shipments.csv')
    if shipments.empty:
        return []
    shipments['risk_group'] = shipments['delay_flag'].apply(lambda val: 'High' if val else 'Low')
    return shipments.groupby('risk_group').size().reset_index(name='count').to_dict(orient='records')


def create_exception(request_data: dict) -> dict:
    exceptions = _load_csv('exceptions.csv')
    next_id = 1 if exceptions.empty else int(len(exceptions)) + 1
    new_exception = {
        'exception_id': next_id,
        'shipment_id': request_data.get('shipment_id', 'N/A'),
        'exception_reason': request_data.get('exception_reason', 'Other'),
        'exception_type': request_data.get('exception_type', 'Operational Delay'),
        'severity': request_data.get('severity', 'Medium'),
        'status': request_data.get('status', 'Open'),
        'created_at': pd.Timestamp.now().isoformat(),
        'resolved_at': '',
        'assigned_to': request_data.get('assigned_to', 'Ops Team'),
        'notes': request_data.get('notes', '')
    }
    exceptions = pd.concat([exceptions, pd.DataFrame([new_exception])], ignore_index=True)
    out_path = DATA_DIR / 'exceptions.csv'
    exceptions.to_csv(out_path, index=False)
    return new_exception
