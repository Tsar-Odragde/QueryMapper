from app import create_app

app = create_app()

if __name__ == "__main__":
    # Local dev
    port = app.config.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
