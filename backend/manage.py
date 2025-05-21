#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import requests
import os, sys

def check_ollama():
    try:
        response = requests.get("http://localhost:11434")
        if response.status_code != 200:
            raise Exception(f"返回状态码: {response.status_code}")
    except Exception as e:
        print(f"Ollama连接失败", end=" ")
        sys.exit(1)
    print("Ollama连接成功")

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    check_ollama()
    main()
