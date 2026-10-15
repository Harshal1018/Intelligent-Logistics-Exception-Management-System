# Intelligent Logistics Exception Management System

A portfolio project for a fresher B.Tech Electronics and Computer Science graduate, designed to demonstrate end-to-end understanding of business analysis, data analysis, SQL, Power BI, Python, machine learning, and full-stack application development.

## Business Problem

A logistics company handles thousands of shipments daily. Operational delays arise from hub congestion, route disruptions, weather conditions, wrong addresses, failed deliveries, vehicle breakdowns, sorting delays, and other exceptions. The business needs a centralized platform to monitor shipments, track operational exceptions, monitor SLA adherence, analyze root causes, compare hub and carrier performance, and predict shipment delays before they happen.

## Objectives

- Track shipment lifecycle status.
- Record and manage logistics exceptions.
- Measure SLA compliance.
- Identify recurrent delay causes.
- Benchmark hubs and carriers.
- Predict shipment delay risk.
- Recommend operational actions.
- Provide management dashboards and exception monitoring.

<img width="1905" height="891" alt="Screenshot 2026-10-15 120303" src="https://github.com/user-attachments/assets/ee696e40-157c-481a-90b8-d1d715be10bd" />
<img width="1911" height="899" alt="Screenshot 2026-10-15 115840" src="https://github.com/user-attachments/assets/e5870061-07d9-4ca4-9680-4be1ef14302c" />
<img width="1900" height="768" alt="Screenshot 2026-10-15 120044" src="https://github.com/user-attachments/assets/fe75720e-820d-4eb4-9e1e-b4bc99267905" />
<img width="1865" height="891" alt="Screenshot 2026-10-15 120124" src="https://github.com/user-attachments/assets/b7b21459-1be4-49f5-9ff6-7f39a8096ef9" />
<img width="1901" height="863" alt="Screenshot 2026-10-15 120224" src="https://github.com/user-attachments/assets/acd017db-3a89-4da5-9361-6d130c8beef2" />
<img width="1896" height="867" alt="Screenshot 2026-10-15 120244" src="https://github.com/user-attachments/assets/e4da3e35-2017-4c9f-b79d-fd0bcc13cce8" />



## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: MySQL
- Data Analysis: Python, Pandas, NumPy
- Machine Learning: Scikit-learn
- Visualization: Power BI design specification

## Repository Structure

```text
.
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── data_service.py
│   ├── ml_service.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
├── scripts/
│   ├── analyze_data.py
│   ├── create_mysql_schema.sql
│   ├── generate_data.py
│   └── train_model.py
├── docs/
│   ├── business_requirements.md
│   ├── process_analysis.md
│   ├── powerbi_dashboard_spec.md
│   ├── business_insights.md
│   └── rtm.md
├── tests/
│   ├── test_app.py
│   └── test_cases.md
├── data/
│   ├── generated/
│   └── reports/
└── model/
    └── delay_model.joblib
```

## How to Run

### 1. Create a virtual environment

```bash
python -m venv .venv
. .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate synthetic data

```bash
python scripts/generate_data.py
```

### 4. Load schema to MySQL

Import the SQL script in MySQL Workbench or command line:

```bash
mysql -u <username> -p < scripts/create_mysql_schema.sql
```

### 5. Train the delay prediction model

```bash
python scripts/train_model.py
```

### 6. Run the Flask application

```bash
python -m app
```

Then open:

```text
http://127.0.0.1:5000/
```

## Business Scope Included

- Shipment tracking and lifecycle management
- Exception log and assignment workflow
- SLA breach monitoring
- Delay cause analysis
- Hub and carrier benchmarking
- Machine learning-based delay risk prediction
- Management dashboard concepts
- Testing and traceability documentation

## Scope Limitations

This is a realistic portfolio project intended to demonstrate analytical and engineering capability. It does not claim enterprise-grade production readiness, full-scale security controls, or multi-region operational deployment.

## Future Enhancements

- Real-time shipment tracking integration
- IoT/telemetry-based route monitoring
- Alerting and email notifications
- Role-based access control
- Auto-assignment rules for exceptions
- Deployment with Docker and CI/CD
- Advanced ensemble ML models

## Expected Portfolio Outcome

The project demonstrates a full lifecycle from business requirement to analytical insight to actionable software solution, making it suitable for an interview, resume, and GitHub portfolio.
