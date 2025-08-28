import secrets
from flask import Blueprint, current_app, jsonify, redirect, request, session
from sqlalchemy import select
from ..db import SessionLocal
from ..models import OAuthToken
from ..services.meli_oauth import build_authorize_url, exchange_code_for_token, refresh_access_token, compute_expiry

oauth_bp = Blueprint("oauth", __name__)

def _require_env():
    miss = [k for k in ("MELI_CLIENT_ID","MELI_CLIENT_SECRET","MELI_REDIRECT_URI") if not current_app.config.get(k)]
    return None if not miss else f"Missing env vars: {', '.join(miss)}"

@oauth_bp.get("/login")
def login():
    err = _require_env()
    if err: return jsonify({"error": err}), 500
    state = secrets.token_urlsafe(24)
    session["oauth_state"] = state
    return redirect(build_authorize_url(current_app, state))

@oauth_bp.get("/callback")
def callback():
    err = _require_env()
    if err: return jsonify({"error": err}), 500

    code  = request.args.get("code")
    state = request.args.get("state")
    if not code or not state or state != session.get("oauth_state"):
        return jsonify({"error": "Invalid or missing code/state"}), 400
    session.pop("oauth_state", None)

    try:
        token_payload = exchange_code_for_token(current_app, code)
    except Exception as e:
        return jsonify({"error": "token_exchange_failed", "detail": str(e)}), 400

    meli_user_id = str(token_payload.get("user_id") or "")
    expires_in   = int(token_payload.get("expires_in", 0) or 0)

    with SessionLocal() as db:
        row = db.execute(select(OAuthToken).where(OAuthToken.meli_user_id == meli_user_id)).scalar_one_or_none()
        if not row:
            row = OAuthToken(meli_user_id=meli_user_id)
            db.add(row)

        row.access_token  = token_payload.get("access_token", "")
        # refresh_token may not be returned every time; keep old if absent
        rt = token_payload.get("refresh_token")
        if rt: row.refresh_token = rt
        row.token_type    = token_payload.get("token_type")
        row.scope         = token_payload.get("scope")
        row.expires_at    = compute_expiry(expires_in)
        db.commit()

    return jsonify({
        "linked": True,
        "meli_user_id": meli_user_id,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None
    }), 200

@oauth_bp.post("/refresh")
def refresh():
    body = request.get_json(silent=True) or {}
    meli_user_id = str(body.get("meli_user_id", ""))
    if not meli_user_id:
        return jsonify({"error": "meli_user_id required"}), 400

    with SessionLocal() as db:
        row = db.execute(select(OAuthToken).where(OAuthToken.meli_user_id == meli_user_id)).scalar_one_or_none()
        if not row or not row.refresh_token:
            return jsonify({"error": "no_refresh_token"}), 400

        try:
            payload = refresh_access_token(current_app, row.refresh_token)
        except Exception as e:
            return jsonify({"error": "refresh_failed", "detail": str(e)}), 400

        row.access_token = payload.get("access_token", "")
        if payload.get("refresh_token"):
            row.refresh_token = payload["refresh_token"]
        expires_in = int(payload.get("expires_in", 0) or 0)
        row.expires_at = compute_expiry(expires_in)
        row.token_type = payload.get("token_type", row.token_type)
        row.scope      = payload.get("scope", row.scope)
        db.commit()

    return jsonify({"refreshed": True}), 200
