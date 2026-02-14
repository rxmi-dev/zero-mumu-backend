from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # FIX: Allow all origins during development
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app