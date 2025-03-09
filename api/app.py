"""
Development server for PL4M API.

This module provides a development server with debug mode and CORS support.
"""

from flask import Flask
from flask_cors import CORS
from pl4m_utils.api import content_bp
import os

def create_dev_app():
    """Create Flask app with development configuration."""
    app = Flask(__name__)
    
    # Register the API blueprint
    app.register_blueprint(content_bp)
    
    # Enable CORS for development
    CORS(app)
    
    # Development configuration
    app.config.update(
        DEBUG=True,
        ENV='development'
    )
    
    return app

def main():
    """Run the development server."""
    port = int(os.environ.get('PORT', 8887))
    app = create_dev_app()
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main() 