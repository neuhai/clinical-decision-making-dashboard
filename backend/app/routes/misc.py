from flask import Blueprint, jsonify, current_app

bp = Blueprint('misc', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({
        "status": "ok",
        "message": "Server is running"
    })

@bp.route('/debug/routes', methods=['GET'])
def list_routes():
    """List all registered routes in the application."""
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    return jsonify(routes) 