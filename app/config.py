import os
import secrets

def load_config(app):
    app.config["MELI_CLIENT_ID"]     = os.getenv("MELI_CLIENT_ID", "")
    app.config["MELI_CLIENT_SECRET"] = os.getenv("MELI_CLIENT_SECRET", "")
    app.config["MELI_REDIRECT_URI"]  = os.getenv("MELI_REDIRECT_URI", "http://localhost:8000/callback")
    app.config["MELI_AUTHORIZE_URL"] = os.getenv("MELI_AUTHORIZE_URL", "https://auth.mercadolibre.com.ar/authorization")
    app.config["MELI_TOKEN_URL"]     = os.getenv("MELI_TOKEN_URL", "https://api.mercadolibre.com/oauth/token")

    app.config["DATABASE_URL"]       = os.getenv("DATABASE_URL", "sqlite:///tokens.db")
    app.config["PORT"]               = int(os.getenv("PORT", "8000"))

    # Flask session/CSRF state storage
    app.config["SECRET_KEY"]         = os.getenv("FLASK_SECRET_KEY", secrets.token_urlsafe(32))
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # Set True on HTTPS envs:
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
