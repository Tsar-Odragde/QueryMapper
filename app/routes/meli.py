from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from sqlalchemy import select
from ..db import SessionLocal
from ..models import OAuthToken
from ..services.meli_oauth import get_me

meli_bp = Blueprint("meli", __name__)

@meli_bp.get("/meli/me")
def me():
    meli_user_id = request.args.get("meli_user_id", "")
    if not meli_user_id:
        return jsonify({"error": "meli_user_id required"}), 400

    with SessionLocal() as db:
        row = db.execute(select(OAuthToken).where(OAuthToken.meli_user_id == meli_user_id)).scalar_one_or_none()
        if not row:
            return jsonify({"error": "not_linked"}), 401

        if not row.expires_at or row.expires_at < datetime.now(timezone.utc):
            return jsonify({"error": "expired", "action": "POST /refresh"}), 401

        data, code = get_me(row.access_token)
        return (data, code)
