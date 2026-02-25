import os
from flask import Flask, request, jsonify, redirect
from database import db
from models import ShortURL
from utils import generate_code


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Create short URL
    @app.post("/api/shorten")
    def shorten():
        data = request.get_json(silent=True) or {}
        original_url = (data.get("url") or "").strip()

        if not original_url:
            return jsonify({"error": "url is required"}), 400
        if not (original_url.startswith("http://") or original_url.startswith("https://")):
            return jsonify({"error": "url must start with http:// or https://"}), 400

        # generate unique code (retry a few times just in case)
        code = None
        for _ in range(10):
            candidate = generate_code(7)
            exists = ShortURL.query.filter_by(code=candidate).first()
            if not exists:
                code = candidate
                break

        if not code:
            return jsonify({"error": "failed to generate unique code"}), 500

        short = ShortURL(code=code, original_url=original_url)
        db.session.add(short)
        db.session.commit()

        base_url = request.host_url.rstrip("/")
        short_url = f"{base_url}/{code}"

        return jsonify(
            {
                "code": code,
                "short_url": short_url,
                "original_url": original_url,
                "clicks": short.clicks,
                "created_at": short.created_at.isoformat() + "Z",
            }
        ), 201

    # Redirect by code
    @app.get("/<string:code>")
    def go(code: str):
        short = ShortURL.query.filter_by(code=code).first()
        if not short:
            return jsonify({"error": "short url not found"}), 404

        short.clicks += 1
        db.session.commit()

        return redirect(short.original_url, code=302)

    # Get info about a short url
    @app.get("/api/info/<string:code>")
    def info(code: str):
        short = ShortURL.query.filter_by(code=code).first()
        if not short:
            return jsonify({"error": "short url not found"}), 404

        base_url = request.host_url.rstrip("/")
        return jsonify(
            {
                "code": short.code,
                "short_url": f"{base_url}/{short.code}",
                "original_url": short.original_url,
                "clicks": short.clicks,
                "created_at": short.created_at.isoformat() + "Z",
            }
        ), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
