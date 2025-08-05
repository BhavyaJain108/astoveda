#!/usr/bin/env python3
"""
Astroveda Quiz System - Entry Point

A Flask-based quiz application with modular architecture.
"""

import os
import signal
import sys
from quiz import create_app

def find_and_kill_existing_process():
    """Find and kill any existing Flask processes on port 8000."""
    try:
        # Find process using port 8000
        import subprocess
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Killed existing process {pid}")
                except (ProcessLookupError, ValueError):
                    pass
    except Exception as e:
        print(f"Note: Could not check for existing processes: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\nShutting down gracefully...')
    sys.exit(0)

# Create the Flask application
app = create_app('development')

# Debug: Print registered routes
print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    
    # Only kill existing processes if this is the main process (not auto-reload)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        find_and_kill_existing_process()
        print("Starting Flask app on http://127.0.0.1:8000")
    
    try:
        app.run(debug=True, port=8000)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port 8000 is still in use. Trying to force kill and restart...")
            find_and_kill_existing_process()
            import time
            time.sleep(1)
            app.run(debug=True, port=8000)
        else:
            raise