#!/usr/bin/env python3
"""
Entry point script to run the Factify API server.
This script should be run from the project root directory.
"""

if __name__ == '__main__':
    from api.app import create_app
    
    app = create_app()
    print("Starting Factify API server...")
    print("API will be available at: http://127.0.0.1:5000")
    print("Health check endpoint: http://127.0.0.1:5000/health")
    app.run(debug=True, port=5000) 