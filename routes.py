from flask import Blueprint, abort, redirect, render_template, request, send_file, url_for

from app.data_service import (
    create_exception,
    get_dashboard_metrics,
    get_exception_queue,
    get_risk_summary,
    get_shipment_by_id,
    get_shipments,
    search_shipments,
)
from app.ml_service import predict_shipment_delay
from app.pdf_service import generate_shipment_pdf

routes = Blueprint('routes', __name__)


@routes.route('/')
def login_page():
    return render_template('login.html')


@routes.route('/dashboard')
def dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard.html', metrics=metrics)


@routes.route('/shipments')
def shipments_page():
    shipments = get_shipments(limit=100)
    return render_template('shipments.html', shipments=shipments)


@routes.route('/shipments/search', methods=['GET'])
def search_page():
    query = request.args.get('q', '')
    shipments = search_shipments(query)
    return render_template('shipments.html', shipments=shipments, query=query)


@routes.route('/shipments/<shipment_id>')
def shipment_detail(shipment_id):
    shipment = get_shipment_by_id(shipment_id)
    prediction = predict_shipment_delay(shipment or {})
    return render_template('shipment_detail.html', shipment=shipment, prediction=prediction)


@routes.route('/shipments/<shipment_id>/pdf')
def shipment_pdf(shipment_id):
    shipment = get_shipment_by_id(shipment_id)
    if shipment is None:
        abort(404)

    prediction = predict_shipment_delay(shipment)
    pdf = generate_shipment_pdf(shipment, prediction)
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'shipment-{shipment_id}.pdf',
    )


@routes.route('/exceptions')
def exception_queue():
    exceptions = get_exception_queue()
    return render_template('exception_queue.html', exceptions=exceptions)


@routes.route('/exceptions/create', methods=['GET', 'POST'])
def create_exception_page():
    if request.method == 'POST':
        payload = {
            'shipment_id': request.form.get('shipment_id'),
            'exception_reason': request.form.get('exception_reason'),
            'exception_type': request.form.get('exception_type'),
            'severity': request.form.get('severity'),
            'status': request.form.get('status'),
            'assigned_to': request.form.get('assigned_to'),
            'notes': request.form.get('notes'),
        }
        create_exception(payload)
        return redirect(url_for('routes.exception_queue'))
    return render_template('exception_detail.html', exception=None)


@routes.route('/exceptions/<int:exception_id>')
def exception_detail(exception_id):
    from app.data_service import get_exception_by_id

    exception = get_exception_by_id(exception_id)
    return render_template('exception_detail.html', exception=exception)


@routes.route('/risk-prediction')
def risk_prediction_page():
    shipments = get_shipments(limit=20)
    details = []
    for shipment in shipments:
        details.append({**shipment, **predict_shipment_delay(shipment)})
    return render_template('risk_prediction.html', shipments=details)


@routes.route('/analytics')
def analytics_page():
    metrics = get_dashboard_metrics()
    risk_summary = get_risk_summary()
    return render_template('analytics.html', metrics=metrics, risk_summary=risk_summary)


@routes.route('/login', methods=['POST'])
def login_submit():
    return redirect(url_for('routes.dashboard'))
