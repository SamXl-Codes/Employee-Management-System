"""
WorkFlowX - Application Entry Point

This is the main entry point for the Flask application.
It imports the app and routes, then runs the server.
"""

from app import app
import routes  # noqa: F401 - Import routes to register them with the app
import socket

def get_local_ip():
    """Automatically detect the local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    # Run the Flask development server
    # In production, gunicorn will be used instead
    network_ip = get_local_ip()
    print("🚀 Starting WorkFlowX")
    print("   Local:   http://127.0.0.1:8080")
    print(f"   Network: http://{network_ip}:8080")
    print("   Scan QR with phone on same WiFi network!")
    app.run(host='0.0.0.0', port=8080, debug=True)
