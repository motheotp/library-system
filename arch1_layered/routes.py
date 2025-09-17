from flask import Blueprint, jsonify
from services import get_all_users

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/users')
def users():
    users = get_all_users()
    return jsonify([{'id': u.id, 'name': u.name} for u in users])