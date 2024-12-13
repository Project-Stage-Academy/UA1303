#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import psycopg2
from dotenv import load_dotenv


load_dotenv()  

if not os.getenv('VIRTUAL_ENV'):
    print("Warning: It seems like the virtual environment is not activated.")
else:
    print("Virtual environmet activated")

def check_database_connection():
    """Перевірка з'єднання з базою даних."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )
        conn.close()
        print("Database connection successful.")
    except Exception as e:
        print("Database connection error:", e)
        exit(1)  



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')
    check_database_connection()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
