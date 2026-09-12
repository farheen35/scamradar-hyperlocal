"""
app.py - ScamRadar Flask Application & REST API
Provides backend services for AI scam analysis, community reporting,
interactive map data, dashboard metrics, and alert management.
"""

import os
from flask import Flask, render_template, request, jsonify
import database
import ai_engine

# Initialize Flask with custom template and static folders
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "app", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "app", "static")
)

# Ensure database is initialized at app launch
with app.app_context():
    database.init_db()

@app.route("/")
def index():
    """Renders the main single-page application."""
    return render_template("index.html")

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns aggregated report and risk statistics for the dashboard."""
    try:
        stats = database.get_stats()
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve statistics. Please try again later."
        }), 500

@app.route("/api/reports", methods=["GET"])
def get_reports():
    """Fetches reports with optional filters (category, risk_level, area, limit)."""
    try:
        category = request.args.get("category", default=None)
        risk_level = request.args.get("risk_level", default=None)
        area = request.args.get("area", default=None)
        limit = int(request.args.get("limit", default=100))

        reports = database.get_reports(category=category, risk_level=risk_level, area=area, limit=limit)
        return jsonify({
            "success": True,
            "count": len(reports),
            "data": reports
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to load community reports. Please try again."
        }), 500

@app.route("/api/reports", methods=["POST"])
def create_report():
    """
    Submits a new community report.
    Validates payload, auto-analyzes risk if missing, saves to SQLite,
    and updates dynamic community alerts.
    """
    try:
        payload = request.get_json(silent=True) or {}
        description = payload.get("description", "").strip()
        area = payload.get("area", "").strip()
        category = payload.get("category", "").strip()

        # Validation
        if not description:
            return jsonify({
                "success": False,
                "error": "Message or description cannot be empty."
            }), 400

        if len(description) < 10:
            return jsonify({
                "success": False,
                "error": "Please provide a more descriptive message (at least 10 characters)."
            }), 400

        if len(description) > 5000:
            return jsonify({
                "success": False,
                "error": "Message description is too long (maximum 5,000 characters)."
            }), 400

        if not area:
            area = "Hyderabad (General)"

        # Auto-analyze risk with AI engine if not supplied or verifying
        analysis = ai_engine.analyze_message(description)
        risk_level = payload.get("risk_level") or analysis.get("risk_level", "WATCH")
        risk_score = payload.get("risk_score")
        if risk_score is None:
            risk_score = analysis.get("risk_score", 30)
        else:
            risk_score = int(risk_score)

        if not category or category == "Other" or category == "Select Category":
            category = analysis.get("category", "Other / Suspicious Message")

        lat = payload.get("latitude")
        lng = payload.get("longitude")
        if lat is not None:
            lat = float(lat)
        if lng is not None:
            lng = float(lng)

        # Persist to database
        saved_report = database.add_report(
            category=category,
            description=description,
            risk_level=risk_level,
            risk_score=risk_score,
            area=area,
            latitude=lat,
            longitude=lng,
            source="community_report"
        )

        return jsonify({
            "success": True,
            "message": "Report added successfully. Your report can help warn other people in your community.",
            "data": saved_report
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "An error occurred while saving your report. Please try again."
        }), 500

@app.route("/api/analyze", methods=["POST"])
def analyze_scam():
    """
    Evaluates suspicious text using the local explainable AI engine.
    Returns risk level, calibrated score, detected red flags, explanation,
    and actionable safety recommendations.
    """
    try:
        payload = request.get_json(silent=True) or {}
        text = payload.get("text", "").strip()

        if not text:
            return jsonify({
                "success": False,
                "error": "Please enter or paste a suspicious message to analyze."
            }), 400

        if len(text) > 5000:
            return jsonify({
                "success": False,
                "error": "Message text is too long (maximum 5,000 characters)."
            }), 400

        result = ai_engine.analyze_message(text)
        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Analysis could not be completed. Please try again."
        }), 500

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Fetches real-time community alerts derived from clustered report patterns."""
    try:
        alerts = database.get_alerts()
        return jsonify({
            "success": True,
            "count": len(alerts),
            "data": alerts
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch community alerts."
        }), 500

@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Fetches user preferences."""
    try:
        settings = database.get_settings()
        return jsonify({
            "success": True,
            "data": settings
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to load preferences."
        }), 500

@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Updates user preferences."""
    try:
        payload = request.get_json(silent=True) or {}
        for key, val in payload.items():
            database.update_setting(str(key), str(val))
        return jsonify({
            "success": True,
            "message": "Preferences updated successfully."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to save preferences."
        }), 500

# Global 404 handler
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404

# Global 500 handler
@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error. Please try again."}), 500


if __name__ == "__main__":
    # Run locally on 127.0.0.1:5000
    print("Starting ScamRadar Server at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
