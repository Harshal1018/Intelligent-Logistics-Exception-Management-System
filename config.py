from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = 'logistics-portfolio-demo-key'
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'generated'
    JSON_SORT_KEYS = False

    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'logistics_exception_db'
    DB_PORT = '3306'

    POWER_BI_REPORT_PATH = BASE_DIR / 'docs' / 'powerbi_dashboard_spec.md'
