"""
WorkFlowX - Application Entry Point

This is the main entry point for the Flask application.
It imports the app and routes, then runs the server.
"""

from app import app
import routes  # noqa: F401 - Import routes to register them with the app

if __name__ == "__main__":
    # Run the Flask development server
    # In production, gunicorn will be used instead
    app.run(host='0.0.0.0', port=5000, debug=True)
