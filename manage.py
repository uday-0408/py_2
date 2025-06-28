#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess


def start_docker_container():
    container_name = "code-runner"

    # Check if the container is already running
    try:
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", f"name={container_name}"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            print(f"✅ Docker container '{container_name}' is already running.")
        else:
            # If not running, try to start it (or run it if not created yet)
            print(f"🚀 Starting Docker container '{container_name}'...")
            subprocess.run(
                ["docker", "start", container_name],  # assumes it was created before
                check=True,
            )
    except Exception as e:
        print(f"⚠️ Failed to start Docker container '{container_name}': {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "compiler.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Start Docker container only if running the Django server
    if len(sys.argv) >= 2 and sys.argv[1] == "runserver":
        start_docker_container()

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
