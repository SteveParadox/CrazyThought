from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return jsonify({'error': '404 Not Found'}), 404


@errors.app_errorhandler(403)
def error_403(error):
    return jsonify({'error': '403 Forbidden'}), 403


@errors.app_errorhandler(500)
def error_500(error):
    return jsonify({'error': '500 Internal Server Error'}), 500


@errors.app_errorhandler(418)
def error_418(error):
    return jsonify({'error': "I'm a teapot"}), 418
