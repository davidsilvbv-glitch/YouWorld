from flask import jsonify, request

from . import auth_bp
from ..auth import AuthError, get_current_user, login_user, logout_user, upsert_google_user, verify_google_token


@auth_bp.route('/google', methods=['POST'])
def google_login():
    data = request.get_json() or {}
    credential = data.get('credential')
    if not credential:
        return jsonify({'success': False, 'error': 'credential_required'}), 400
    try:
        payload = verify_google_token(credential)
        user = upsert_google_user(payload)
        login_user(user)
        return jsonify({'success': True, 'data': {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'avatar_url': user.avatar_url,
            'email_verified': user.email_verified,
        }})
    except AuthError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 401


@auth_bp.route('/me', methods=['GET'])
def me():
    user = get_current_user()
    if not user:
        return jsonify({'success': True, 'data': None})
    return jsonify({'success': True, 'data': {
        'user_id': user.user_id,
        'email': user.email,
        'name': user.name,
        'avatar_url': user.avatar_url,
        'email_verified': user.email_verified,
    }})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'success': True})
