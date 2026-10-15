from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data' / 'generated'
MODEL_DIR = ROOT / 'model'
MODEL_DIR.mkdir(exist_ok=True)

shipments = pd.read_csv(DATA_DIR / 'shipments.csv')
exceptions = pd.read_csv(DATA_DIR / 'exceptions.csv')

shipment_exception_counts = exceptions.groupby('shipment_id').size().reset_index(name='previous_exceptions')
shipments = shipments.merge(shipment_exception_counts, on='shipment_id', how='left').fillna({'previous_exceptions': 0})

carrier_delay = shipments.groupby('carrier_id')['delay_flag'].mean().reset_index().rename(columns={'delay_flag': 'carrier_delay_rate'})
hub_delay = shipments.groupby('origin_hub_id')['delay_flag'].mean().reset_index().rename(columns={'delay_flag': 'hub_delay_rate'})
shipments = shipments.merge(carrier_delay, on='carrier_id', how='left')
shipments = shipments.merge(hub_delay, on='origin_hub_id', how='left')

feature_cols = [
    'distance_km',
    'weight_kg',
    'carrier_id',
    'origin_hub_id',
    'destination_hub_id',
    'shipment_type',
    'priority',
    'carrier_delay_rate',
    'hub_delay_rate',
    'previous_exceptions',
    'sla_hours',
]

X = shipments[feature_cols]
y = shipments['delay_flag']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

cat_features = ['carrier_id', 'origin_hub_id', 'destination_hub_id', 'shipment_type', 'priority']
num_features = [col for col in feature_cols if col not in cat_features]

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), num_features),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features),
])

logistic_model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=2000, class_weight='balanced')),
])

rf_model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')),
])

for name, model in [('logistic_regression', logistic_model), ('random_forest', rf_model)]:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_prob),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
    }
    print(f'\nModel: {name}')
    for metric_name, value in metrics.items():
        print(f'{metric_name}: {value}')

    model_path = MODEL_DIR / f'{name}.joblib'
    joblib.dump(model, model_path)
    print(f'Saved model to {model_path}')

selected_model = logistic_model
joblib.dump(selected_model, MODEL_DIR / 'delay_model.joblib')
print(f'Default model saved as {MODEL_DIR / "delay_model.joblib"}')
