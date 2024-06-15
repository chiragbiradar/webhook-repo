from flask import Blueprint, json, request, jsonify, render_template
from datetime import datetime
from ..extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


@webhook.route('/receiver', methods=["POST"])
def reciever():
    if request.content_type != 'application/json':
        return jsonify({"message": "Content-Type must be application/json"}), 415
    
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == "push":
        event = {
            "request_id": data['head_commit']['id'],
            "type": "push",
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
            "timestamp": datetime.utcnow()
        }
    elif event_type == "pull_request":
        if data['action'] == 'opened':
            event = {
                "request_id": data['pull_request']['id'],
                "type": "pull_request",
                "author": data['pull_request']['user']['login'],
                "from_branch": data['pull_request']['head']['ref'],
                "to_branch": data['pull_request']['base']['ref'],
                "timestamp": datetime.utcnow()
            }
        elif data['action'] == "closed" and data['pull_request']['merged']:
            event = {
                "request_id": data['pull_request']['id'],
                "type": "merge",
                "author": data['pull_request']['user']['login'],
                "from_branch": data['pull_request']['head']['ref'],
                "to_branch": data['pull_request']['base']['ref'],
                "timestamp": datetime.utcnow()
            }
        else:
            return jsonify({"message": "Event type not handled"}), 200
    else:
        return jsonify({"message": "Event type not handled"}), 200

    mongo.db.events.insert_one(event)
    return jsonify({"message": "Event received"}), 201



@webhook.route('/')
def index():
    return render_template('index.html')

@webhook.route('/events', methods=["GET"])
def get_events():
    events = list(mongo.db.events.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)



