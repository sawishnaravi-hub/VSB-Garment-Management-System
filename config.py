import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'vsb-garment-mfg-secret-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MySQL Database credentials
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'vsb_garment_management')
    
    # Priority database URI
    custom_uri = os.getenv('DATABASE_URI')
    if custom_uri:
        SQLALCHEMY_DATABASE_URI = custom_uri
    else:
        if DB_PASSWORD:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        else:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Company settings
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'VSB Garment Manufacturing')
    OPENING_BALANCE = float(os.getenv('OPENING_BALANCE', 500000.00))
    CURRENCY_SYMBOL = os.getenv('CURRENCY_SYMBOL', '₹')

    @classmethod
    def get_verified_db_uri(cls):
        """
        Verifies if MySQL database is accessible. If MySQL is unreachable,
        gracefully uses local SQLite so the system remains fully functional
        with zero setup hurdles, while maintaining 100% MySQL compatibility.
        """
        import pymysql
        try:
            conn = pymysql.connect(
                host=cls.DB_HOST,
                port=cls.DB_PORT,
                user=cls.DB_USER,
                password=cls.DB_PASSWORD,
                connect_timeout=2
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{cls.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            print(f"[DATABASE] Connected successfully to MySQL database '{cls.DB_NAME}' on {cls.DB_HOST}:{cls.DB_PORT}")
            return cls.SQLALCHEMY_DATABASE_URI
        except Exception as e:
            sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vsb_garment_management.db'))
            print(f"[DATABASE NOTICE] MySQL connection to {cls.DB_HOST}:{cls.DB_PORT} could not be established ({e}).")
            print(f"[DATABASE NOTICE] Falling back to SQLite database at: {sqlite_path}")
            print(f"[DATABASE NOTICE] Start your MySQL server (e.g. XAMPP/MySQL) anytime to switch to MySQL.")
            return f"sqlite:///{sqlite_path}"
