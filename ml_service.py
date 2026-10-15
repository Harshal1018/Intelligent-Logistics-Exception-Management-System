from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / 'model'


def _safe_probability(raw_value: float) -> float:
    return max(0.0, min(1.0, float(raw_value)))


def get_default_prediction(shipment: dict) -> dict:
    distance = float(shipment.get('distance_km', 1000))
    weight = float(shipment.get('weight_kg', 15))
    sla = float(shipment.get('sla_hours', 48))
    priority_score = {'Normal': 0.0, 'Priority': 0.12, 'VIP': 0.22}.get(shipment.get('priority', 'Normal'), 0.0)
    base_probability = 0.08 + (distance / 5000) * 0.25 + (weight / 80) * 0.1 + priority_score + (1 / max(1, sla)) * 0.12
    probability = min(0.95, max(0.05, base_probability))
    return {
        'delay_probability': round(probability * 100, 1),
        'risk_category': 'HIGH' if probability > 0.7 else 'MEDIUM' if probability > 0.4 else 'LOW',
        'recommended_action': (
            'Prioritize the shipment for operational review.' if probability > 0.7 else
            'Monitor the shipment closely with proactive intervention.' if probability > 0.4 else
            'Continue standard monitoring.'
        )
    }


def predict_shipment_delay(shipment: dict) -> dict:
    model_path = MODEL_DIR / 'delay_model.joblib'
    if not model_path.exists():
        return get_default_prediction(shipment)

    try:
        model = joblib.load(model_path)
        feature_row = pd.DataFrame([
            {
                'distance_km': float(shipment.get('distance_km', 1000)),
                'weight_kg': float(shipment.get('weight_kg', 15)),
                'carrier_id': shipment.get('carrier_id', 'CAR002'),
                'origin_hub_id': shipment.get('origin_hub_id', 'HUB001'),
                'destination_hub_id': shipment.get('destination_hub_id', 'HUB002'),
                'shipment_type': shipment.get('shipment_type', 'Standard'),
                'priority': shipment.get('priority', 'Normal'),
                'carrier_delay_rate': float(shipment.get('carrier_delay_rate', 0.18)),
                'hub_delay_rate': float(shipment.get('hub_delay_rate', 0.15)),
                'previous_exceptions': int(shipment.get('previous_exceptions', 0)),
                'sla_hours': float(shipment.get('sla_hours', 48)),
            }
        ])
        probability = model.predict_proba(feature_row)[0, 1]
        probability = _safe_probability(probability)
        risk_category = 'HIGH' if probability >= 0.7 else 'MEDIUM' if probability >= 0.4 else 'LOW'
        if risk_category == 'HIGH':
            action = 'Prioritize the shipment for operational review.'
        elif risk_category == 'MEDIUM':
            action = 'Escalate to the route operations team for watchlist monitoring.'
        else:
            action = 'Continue standard monitoring; no urgent intervention required.'
        return {
            'delay_probability': round(probability * 100, 1),
            'risk_category': risk_category,
            'recommended_action': action,
        }
    except Exception:
        return get_default_prediction(shipment)
