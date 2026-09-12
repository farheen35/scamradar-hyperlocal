"""
database.py - SQLite Database Management for ScamRadar
Handles persistent storage for reports, synthetic demo seeding, and community alerts.
Data survives page refreshes, browser reboots, and Flask server restarts.
"""

import os
import sqlite3
import random
from datetime import datetime, timezone

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "scamradar.db")

# Standard coordinates for Hyderabad neighborhoods (Approximate for privacy)
HYDERABAD_LOCALITIES = {
    "Madhapur": (17.4483, 78.3915),
    "Banjara Hills": (17.4156, 78.4350),
    "Gachibowli": (17.4401, 78.3489),
    "Ameerpet": (17.4375, 78.4482),
    "Kukatpally": (17.4938, 78.3995),
    "Secunderabad": (17.4399, 78.4983),
    "Hitec City": (17.4435, 78.3772),
    "Charminar": (17.3616, 78.4747),
    "Kondapur": (17.4699, 78.3578),
    "Begumpet": (17.4447, 78.4664),
    "Jubilee Hills": (17.4319, 78.4073),
    "Dilsukhnagar": (17.3688, 78.5247),
    "Mehdipatnam": (17.3916, 78.4378),
    "Manikonda": (17.4042, 78.3789),
    "Uppal": (17.4056, 78.5591)
}

# Initial synthetic demo reports (Clearly marked as synthetic demo data)
SYNTHETIC_REPORTS = [
    {
        "category": "Electricity Impersonation",
        "description": "Dear consumer, your electricity power will be disconnected at 9:30 PM tonight by TSSPDCL officer because your previous month bill was not updated. Pay immediately at http://bit.ly/ts-power-bill",
        "risk_level": "HIGH RISK",
        "risk_score": 96,
        "area": "Madhapur",
        "days_ago": 1
    },
    {
        "category": "Electricity Impersonation",
        "description": "Urgent notice from Power Board: Electricity connection disconnection order issued for consumer no 849302. Call electricity officer at 98480xxxxx immediately to clear overdue payment.",
        "risk_level": "HIGH RISK",
        "risk_score": 94,
        "area": "Madhapur",
        "days_ago": 2
    },
    {
        "category": "Fake Delivery",
        "description": "India Post alert: Your consignment parcel IN894038 could not be delivered due to incomplete street address. Please update your address and pay ₹25 redelivery fee at http://post-redeliver.top",
        "risk_level": "MEDIUM RISK",
        "risk_score": 68,
        "area": "Gachibowli",
        "days_ago": 1
    },
    {
        "category": "Fake Delivery",
        "description": "BlueDart tracking update: Parcel arrival suspended. Urgent action required within 24 hours to confirm your pin code or package will be returned to sender.",
        "risk_level": "MEDIUM RISK",
        "risk_score": 58,
        "area": "Gachibowli",
        "days_ago": 3
    },
    {
        "category": "Job Scam",
        "description": "Amazon Part-Time Hiring: Earn ₹3,000 to ₹8,000 daily working from home just 1 hour per day by reviewing products. Contact HR Priya on Telegram @amazon_career_tasks. Security deposit ₹500 required.",
        "risk_level": "HIGH RISK",
        "risk_score": 92,
        "area": "Hitec City",
        "days_ago": 1
    },
    {
        "category": "Job Scam",
        "description": "YouTube Video Liking Job: Work from home daily payout ₹2500. Just like 3 videos and send screenshot on WhatsApp. Initial registration fee ₹300 refundable.",
        "risk_level": "HIGH RISK",
        "risk_score": 88,
        "area": "Ameerpet",
        "days_ago": 2
    },
    {
        "category": "Bank Impersonation",
        "description": "Dear SBI Customer, your YONO account has been blocked today due to pending KYC verification. Click http://sbi-kyc-update.xyz to update PAN immediately and resume banking services.",
        "risk_level": "HIGH RISK",
        "risk_score": 95,
        "area": "Banjara Hills",
        "days_ago": 2
    },
    {
        "category": "Bank Impersonation",
        "description": "HDFC Alert: Your NetBanking access is temporarily suspended. Submit your registered mobile OTP at the verification link to avoid permanent freeze.",
        "risk_level": "HIGH RISK",
        "risk_score": 95,
        "area": "Secunderabad",
        "days_ago": 3
    },
    {
        "category": "Prize Scam",
        "description": "Congratulations! Your mobile number has won ₹25,00,000 in KBC All-India Lucky Draw 2026. Contact Rana Pratap Singh on WhatsApp to claim your cheque.",
        "risk_level": "MEDIUM RISK",
        "risk_score": 65,
        "area": "Kukatpally",
        "days_ago": 4
    },
    {
        "category": "Investment Scam",
        "description": "Join VIP Crypto Bull Signals. Guaranteed 200% return in 48 hours with automated arbitrage robot. Minimum investment ₹5,000. 100% risk free.",
        "risk_level": "HIGH RISK",
        "risk_score": 86,
        "area": "Jubilee Hills",
        "days_ago": 4
    },
    {
        "category": "Other / Suspicious Message",
        "description": "Service notice from telecom: Your SIM card e-KYC is expiring. Call customer executive to prevent disconnection.",
        "risk_level": "WATCH",
        "risk_score": 38,
        "area": "Begumpet",
        "days_ago": 5
    }
]

def get_db_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection to the SQLite database with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def geocode_area(area_name: str) -> tuple:
    """
    Returns approximate latitude and longitude for a neighborhood.
    Applies small random offset (~100-300 meters) so markers in same area don't overlap completely.
    """
    area_clean = area_name.strip()
    
    # Try exact or partial match
    matched_coords = None
    for loc_name, coords in HYDERABAD_LOCALITIES.items():
        if loc_name.lower() in area_clean.lower() or area_clean.lower() in loc_name.lower():
            matched_coords = coords
            break
            
    if not matched_coords:
        # Default center of Hyderabad
        matched_coords = (17.3850, 78.4867)

    # Add small jitter for privacy and map usability (prevent stacked pins)
    jitter_lat = random.uniform(-0.004, 0.004)
    jitter_lng = random.uniform(-0.004, 0.004)
    return (round(matched_coords[0] + jitter_lat, 5), round(matched_coords[1] + jitter_lng, 5))

def init_db():
    """Initializes schema and seeds initial synthetic data if database is new."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            area TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL
        )
    """)

    # Create alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            area TEXT NOT NULL,
            report_count INTEGER NOT NULL,
            message TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    conn.commit()

    # Check if reports table has data
    cursor.execute("SELECT COUNT(*) FROM reports")
    count = cursor.fetchone()[0]

    if count == 0:
        # Seed synthetic demo data
        now_ts = int(datetime.now(timezone.utc).timestamp())
        for item in SYNTHETIC_REPORTS:
            lat, lng = geocode_area(item["area"])
            item_ts = now_ts - (item["days_ago"] * 86400) - random.randint(100, 7200)
            created_at_iso = datetime.fromtimestamp(item_ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO reports (category, description, risk_level, risk_score, area, latitude, longitude, created_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["category"],
                item["description"],
                item["risk_level"],
                item["risk_score"],
                item["area"],
                lat,
                lng,
                created_at_iso,
                "synthetic_demo"
            ))

        conn.commit()
        # Seed default settings
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('primary_area', 'Hyderabad (All Zones)')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('alert_sensitivity', 'medium')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('show_synthetic_badge', 'true')")
        conn.commit()

    # Refresh dynamic alerts based on report data
    refresh_alerts(conn)
    conn.close()

def refresh_alerts(conn: sqlite3.Connection):
    """
    Dynamically generates or updates community alerts based on clusters of reports
    by (category, area). Responsible and cautious wording applied.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alerts")

    # Group by category and area where report count >= 2 or high risk reports exist
    cursor.execute("""
        SELECT category, area, risk_level, COUNT(*) as cnt, MAX(risk_score) as max_score
        FROM reports
        GROUP BY category, area
        ORDER BY cnt DESC, max_score DESC
    """)
    groups = cursor.fetchall()

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for g in groups:
        cat = g["category"]
        area = g["area"]
        cnt = g["cnt"]
        r_level = "HIGH RISK" if g["max_score"] >= 70 else ("MEDIUM RISK" if g["max_score"] >= 40 else "WATCH")

        # Create alert if 2 or more reports exist, or if it's a high risk category
        if cnt >= 2 or (r_level == "HIGH RISK" and cnt >= 1):
            title = f"Reported Pattern: {cat} in {area}"
            message = f"{cnt} community report{'s' if cnt > 1 else ''} with similar patterns {'have' if cnt > 1 else 'has'} been logged in the {area} vicinity. Exercise caution with unsolicited demands."

            if cat == "Electricity Impersonation":
                action = "Do not make payments to personal numbers. Discoms do not cut power via SMS links."
            elif cat == "Bank Impersonation":
                action = "Never click SMS links to update KYC or PAN. Visit your bank branch or use the official mobile app."
            elif cat == "Fake Delivery":
                action = "Do not pay redelivery fees on unofficial web links. Verify on official postal trackers."
            elif cat == "Job Scam":
                action = "Legitimate companies do not charge upfront training or registration fees."
            else:
                action = "Verify all unexpected communications independently through verified numbers."

            cursor.execute("""
                INSERT INTO alerts (title, category, risk_level, area, report_count, message, recommended_action, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, cat, r_level, area, cnt, message, action, now_iso))

    conn.commit()

def get_stats() -> dict:
    """Calculates live dashboard statistics from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM reports")
    total_reports = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE risk_level = 'HIGH RISK'")
    high_risk_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE risk_level = 'MEDIUM RISK'")
    medium_risk_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE risk_level = 'WATCH'")
    watch_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts")
    active_alerts_count = cursor.fetchone()[0]

    # Get 5 most recent reports
    cursor.execute("""
        SELECT id, category, description, risk_level, risk_score, area, latitude, longitude, created_at, source
        FROM reports
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_reports = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "total_reports": total_reports,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "watch_count": watch_count,
        "active_alerts_count": active_alerts_count,
        "recent_reports": recent_reports,
        "data_notice": "Community reports include synthetic demo data for evaluation purposes."
    }

def get_reports(category: str = None, risk_level: str = None, area: str = None, limit: int = 100) -> list:
    """Fetches reports with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, category, description, risk_level, risk_score, area, latitude, longitude, created_at, source FROM reports WHERE 1=1"
    params = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if risk_level and risk_level != "All":
        query += " AND risk_level = ?"
        params.append(risk_level)
    if area and area != "All":
        query += " AND area = ?"
        params.append(area)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reports

def add_report(category: str, description: str, risk_level: str, risk_score: int, area: str,
               latitude: float = None, longitude: float = None, source: str = "community_report") -> dict:
    """Inserts a new report, geocodes coordinates if missing, and updates community alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if latitude is None or longitude is None or latitude == 0 or longitude == 0:
        latitude, longitude = geocode_area(area)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO reports (category, description, risk_level, risk_score, area, latitude, longitude, created_at, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, description, risk_level, risk_score, area, latitude, longitude, now_iso, source))

    new_id = cursor.lastrowid
    conn.commit()

    # Re-evaluate alerts
    refresh_alerts(conn)
    conn.close()

    return {
        "id": new_id,
        "category": category,
        "description": description,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "area": area,
        "latitude": latitude,
        "longitude": longitude,
        "created_at": now_iso,
        "source": source
    }

def get_alerts() -> list:
    """Fetches all active community alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, category, risk_level, area, report_count, message, recommended_action, updated_at
        FROM alerts
        ORDER BY report_count DESC, id DESC
    """)
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alerts

def get_settings() -> dict:
    """Returns stored user preferences."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()
    return settings

def update_setting(key: str, value: str) -> bool:
    """Updates or inserts a setting key-value pair."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    print("Initializing ScamRadar SQLite Database...")
    init_db()
    stats = get_stats()
    print(f"Database Initialized! Total Reports: {stats['total_reports']}, High Risk: {stats['high_risk_count']}, Alerts: {stats['active_alerts_count']}")
