"""
HiddenYatra — WSGI Entry Point
Usage: gunicorn wsgi:app
"""
from app import create_app

app = create_app()
