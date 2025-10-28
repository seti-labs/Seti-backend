import os
from app import create_app

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Handle PORT environment variable properly for Render
    # Render automatically sets PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {app.config['DEBUG']}")
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])

