from flask import Flask, render_template
from .extensions import init_db
from app.webhook.routes import webhook
import os


# Creating our flask app
def create_app():

    app = Flask(__name__)
    
    # registering all the blueprints 
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/github_events")
    init_db(app)


    app.register_blueprint(webhook)
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
