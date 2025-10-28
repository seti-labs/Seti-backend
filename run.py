import os
from app import create_app

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Handle PORT environment variable properly for Render
    port_str = os.getenv('PORT')
    if port_str:
        try:
            port = int(port_str)
        except ValueError:
            print(f"Warning: Invalid PORT value '{port_str}', using default 5000")
            port = 5000
    else:
        port = 5000
    
    host = os.getenv('HOST', '0.0.0.0')
    print(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])

