from flask_pymongo import PyMongo # type: ignore

# Setup MongoDB here
mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)
    return mongo.db
