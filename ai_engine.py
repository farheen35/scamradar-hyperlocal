"""
ai_engine.py - Local Explainable Scam Detection Engine
Deterministic rule-based NLP, pattern matching, and weighted risk scoring.
No external API keys or paid services required.
"""

import re
from typing import Dict, List, Any

# Pattern definitions for Red Flags
RED_FLAG_DEFINITIONS = [
    {
        "id": "urgency",
        "name": "Urgency Pressure",
        "description": "Uses artificial time pressure, deadlines, or panic words to force rapid action before you can verify.",
        "weight": 20,
        "regex": r"\b(immediately|urgent|urgently|today|tonight|within\s+\d+\s*(?:hours?|hrs?|mins?|minutes?)|hurry|last\s+chance|deadline|promptly|without\s+delay|instant(?:ly)?)\b",
    },
    {
        "id": "service_threat",
        "name": "Threat of Service or Account Closure",
        "description": "Threatens service cutoff, electricity disconnection, bank account suspension, or legal consequences.",
        "weight": 25,
        "regex": r"\b(disconnect(?:ed|ion)?|power\s+cut|suspend(?:ed|ion)?|block(?:ed)?|deactivat(?:ed|ion)?|terminate(?:d)?|legal\s+action|police\s+case|court\s+notice|warrant|interruption|freeze|frozen)\b",
    },
    {
        "id": "impersonation",
        "name": "Organization / Authority Impersonation",
        "description": "Claims to represent power utility companies, major banks, courier services, or government regulators.",
        "weight": 20,
        "regex": r"\b(electricity\s+officer|electricity\s+department|power\s+board|tsspdcl|bescom|msedcl|tneb|dhbvn|uppcl|sbp|sbi|hdfc|icici|axis\s+bank|rbi|reserve\s+bank|income\s+tax|it\s+dept|trai|customs|cyber\s+crime|police|india\s+post|blue\s+dart|fedex|delhivery)\b",
    },
    {
        "id": "payment_demand",
        "name": "Unsolicited Payment or Transfer Demand",
        "description": "Directs you to make an immediate payment, transfer funds, pay a penalty, or clear an alleged overdue bill.",
        "weight": 25,
        "regex": r"(?:pay\b|send\s+money|transfer|deposit|due\s+bill|outstanding\s+amount|fine|penalty|recharge)[\s\w]*(?:₹|rs\.?|inr|\$|\d{2,})|\b(?:upi\s*id|gpay|phonepe|paytm|qr\s*code|clear\s+dues)\b",
    },
    {
        "id": "suspicious_link",
        "name": "Suspicious Link / Contact Channel",
        "description": "Contains generic shortened links, unverified web links, raw IP addresses, or unofficial contact numbers.",
        "weight": 25,
        "regex": r"(?:https?://[^\s]+|www\.[^\s]+|\bbit\.ly/\w+|\btinyurl\.com/\w+|\bis\.gd/\w+|\bgoo\.gl/\w+|t\.me/\w+|\bwa\.me/\w+|[a-zA-Z0-9.-]+\.(?:xyz|top|club|site|online|live|vip|work|info|tk|ml|apk)\b|\b(?:following\s+link|link\s+below|click\s+here|tap\s+here|this\s+link|given\s+link|web\s+link)\b)",
    },
    {
        "id": "sensitive_info_request",
        "name": "Request for Sensitive Credentials",
        "description": "Asks for confidential security keys such as OTP, PIN, NetBanking password, CVV, or card credentials.",
        "weight": 30,
        "regex": r"\b(otp|one\s+time\s+password|pin\s+code|netbanking\s+password|cvv|expiry\s+date|card\s+number|aadhaar\s+number|pan\s+card\s+details|share\s+password)\b",
    },
    {
        "id": "prize_lottery",
        "name": "Prize / Lottery / Reward Claim",
        "description": "Claims you won an unentered lottery, reward points, cashback, or luxury vehicle.",
        "weight": 20,
        "regex": r"\b(congratulations|congrats|you\s+have\s+won|lucky\s+draw|lottery|cash\s+prize|reward\s+points|unclaimed\s+bonus|claim\s+now|scratch\s+card|crorepati)\b",
    },
    {
        "id": "too_good_to_be_true",
        "name": "Unrealistic Income / Work Offer",
        "description": "Promises high daily income for minimal effort, Telegram video liking tasks, or guaranteed double returns.",
        "weight": 20,
        "regex": r"\b(earn(?:ing|s)?\s+(?:₹|rs\.?|inr)?\s*\d+[\s\w]*(?:daily|per\s+(?:day|month|week)|day|month|week)|work\s+from\s+home|part\s*time\s+job|like\s+youtube\s+videos|task\s+based\s+earning|no\s+investment\s+needed|guaranteed\s+(?:return|profit)|easy\s+money)\b",
    },
    {
        "id": "job_deposit",
        "name": "Upfront Job Fee / Security Deposit",
        "description": "Demands payment for job application fees, laptop security deposits, or onboarding documents.",
        "weight": 25,
        "regex": r"\b(registration\s+fee|security\s+deposit|refundable\s+amount|training\s+charge|laptop\s+deposit|document\s+verification\s+fee|onboarding\s+fee)\b",
    },
    {
        "id": "investment_pressure",
        "name": "High-Pressure Investment / Crypto Pitch",
        "description": "Encourages urgent investment in cryptocurrency, forex trading schemes, or private signal groups.",
        "weight": 20,
        "regex": r"\b(crypto\s+investment|forex\s+trading|double\s+your\s+money|100%\s+guaranteed|vip\s+trading\s+signals?|binary\s+options|arbitrage|withdraw\s+your\s+profit)\b",
    }
]

# Category classifiers based on domain-specific keyword clusters
CATEGORY_PATTERNS = {
    "Electricity Impersonation": [
        r"\b(electricity|power|disconnection|power\s+cut|bill\s+due|tsspdcl|bescom|msedcl|tneb|uppcl|meter|service\s+interruption|helpline\s+number)\b"
    ],
    "Bank Impersonation": [
        r"\b(bank|account|sbi|hdfc|icici|axis|rbi|kyc|pan\s+update|aadhaar|debit\s+card|credit\s+card|dormant|blocked\s+account|netbanking)\b"
    ],
    "Job Scam": [
        r"\b(part\s*time|job\s+offer|daily\s+income|salary|hr\s+manager|telegram\s+task|like\s+videos|data\s+entry|interview|registration\s+fee|hiring)\b"
    ],
    "Fake Delivery": [
        r"\b(delivery|courier|parcel|package|india\s+post|bluedart|fedex|delhivery|address\s+incomplete|redelivery|shipment|tracking\s+id)\b"
    ],
    "Prize Scam": [
        r"\b(lottery|won|winner|cash\s+prize|lucky\s+draw|kbc|kaun\s+banega|congratulations|reward\s+points|bonus|voucher)\b"
    ],
    "Investment Scam": [
        r"\b(investment|crypto|bitcoin|forex|returns|trading|double\s+money|profit|signals|stock\s+tips|vip\s+group)\b"
    ],
    "Phishing": [
        r"\b(login|password|verify\s+your\s+account|click\s+to\s+activate|security\s+alert|unauthorized\s+access|sign\s*in|reset\s+credentials)\b"
    ]
}

def detect_category(text: str, matched_red_flags: List[Dict[str, Any]]) -> str:
    """Identify the primary scam category from keywords and context."""
    text_lower = text.lower()
    scores = {}

    for category, patterns in CATEGORY_PATTERNS.items():
        score = 0
        for pat in patterns:
            matches = re.findall(pat, text_lower, flags=re.IGNORECASE)
            score += len(matches) * 2
        scores[category] = score

    # Additional contextual category bias based on red flag combinations
    rf_ids = {rf["id"] for rf in matched_red_flags}
    if "service_threat" in rf_ids and any(k in text_lower for k in ["electricity", "power", "meter", "connection", "interruption"]):
        scores["Electricity Impersonation"] = scores.get("Electricity Impersonation", 0) + 10
    if "impersonation" in rf_ids and any(k in text_lower for k in ["post", "parcel", "courier", "package", "address"]):
        scores["Fake Delivery"] = scores.get("Fake Delivery", 0) + 8
    if "too_good_to_be_true" in rf_ids or "job_deposit" in rf_ids:
        scores["Job Scam"] = scores.get("Job Scam", 0) + 8
    if "prize_lottery" in rf_ids:
        scores["Prize Scam"] = scores.get("Prize Scam", 0) + 8
    if "investment_pressure" in rf_ids:
        scores["Investment Scam"] = scores.get("Investment Scam", 0) + 8

    # Pick the category with the highest score above zero
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if sorted_categories and sorted_categories[0][1] > 0:
        return sorted_categories[0][0]

    # If general red flags exist but no specific category stands out
    if rf_ids:
        if "suspicious_link" in rf_ids or "sensitive_info_request" in rf_ids:
            return "Phishing"
        return "Other / Suspicious Message"

    return "General / Informational Message"

def generate_recommendations(category: str, red_flag_ids: set) -> List[str]:
    """Generate clear, protective, non-jargon safety actions."""
    recommendations = []

    if "suspicious_link" in red_flag_ids:
        recommendations.append("Do not click any links or download APK files attached to this message.")
    if "payment_demand" in red_flag_ids or "service_threat" in red_flag_ids:
        recommendations.append("Do not send money or make instant UPI transfers under threat of disconnection.")
    if "sensitive_info_request" in red_flag_ids:
        recommendations.append("Never share your OTP, UPI PIN, ATM PIN, or NetBanking password with anyone.")
    
    # Category-specific guidance
    if category == "Electricity Impersonation":
        recommendations.append("Official electricity discoms (like TSSPDCL) never demand bill payment through personal mobile numbers or third-party links.")
        recommendations.append("Verify your outstanding balance only through the official electricity utility app or consumer bill portal.")
    elif category == "Bank Impersonation":
        recommendations.append("Banks never threaten immediate account suspension via SMS or ask for KYC links via text.")
        recommendations.append("Visit your local bank branch or use the official mobile banking app directly.")
    elif category == "Job Scam":
        recommendations.append("Legitimate recruiters never ask for upfront security deposits or task registration fees.")
        recommendations.append("Never participate in paid Telegram review/like tasks; they are designed to trap you in advance-fee schemes.")
    elif category == "Fake Delivery":
        recommendations.append("Postal and courier services do not ask for ₹5–₹50 redelivery fees via shortened web links.")
        recommendations.append("Track your package directly on the carrier's verified official website with your consignment tracking number.")
    elif category == "Prize Scam":
        recommendations.append("You cannot win a lottery or prize for a contest you never purchased tickets for.")
        recommendations.append("Ignore and block messages asking for processing fees or GST to release gift funds.")
    elif category == "Investment Scam":
        recommendations.append("Guaranteed high returns do not exist in legitimate financial markets. Avoid unregulated Telegram/WhatsApp advisors.")

    # Universal safety action
    recommendations.append("If financial loss has occurred, call the National Cyber Crime Helpline at 1930 immediately or visit cybercrime.gov.in.")

    return recommendations

def analyze_message(text: str) -> Dict[str, Any]:
    """
    Main analysis function.
    Evaluates message against explainable rule-based NLP patterns,
    calculates risk score (0-100), detects category, red flags, and explanations.
    """
    if not text or not text.strip():
        return {
            "success": False,
            "error": "Message text cannot be empty."
        }

    clean_text = text.strip()
    clean_lower = clean_text.lower()

    matched_red_flags = []
    total_raw_weight = 0

    # Scan for red flags
    for rf_def in RED_FLAG_DEFINITIONS:
        matches = list(set(re.findall(rf_def["regex"], clean_lower, flags=re.IGNORECASE)))
        if matches:
            # Format readable match strings
            matched_items = [str(m) if isinstance(m, str) else str(m[0]) for m in matches[:3]]
            matched_red_flags.append({
                "id": rf_def["id"],
                "name": rf_def["name"],
                "description": rf_def["description"],
                "weight": rf_def["weight"],
                "detected_snippets": matched_items
            })
            total_raw_weight += rf_def["weight"]

    # Detect category
    category = detect_category(clean_text, matched_red_flags)
    rf_ids = {rf["id"] for rf in matched_red_flags}

    # Calculate calibrated risk score (0-100)
    # Baseline: base weight scaling
    base_score = min(total_raw_weight * 1.1, 75)

    # Multiplier/Boosters for high-danger combinations
    booster = 0
    # Impersonation + Payment + Threat (Classic extortion/disconnection scam like electricity)
    if "service_threat" in rf_ids and "payment_demand" in rf_ids:
        booster += 20
    if "service_threat" in rf_ids and "urgency" in rf_ids:
        booster += 15
    if "suspicious_link" in rf_ids and ("payment_demand" in rf_ids or "service_threat" in rf_ids):
        booster += 12
    if "sensitive_info_request" in rf_ids:
        booster += 25
    if "too_good_to_be_true" in rf_ids and "job_deposit" in rf_ids:
        booster += 25

    computed_score = int(round(base_score + booster))
    risk_score = max(5, min(computed_score, 98)) if matched_red_flags else 10

    # Determine risk level
    if risk_score >= 70:
        risk_level = "HIGH RISK"
    elif risk_score >= 40:
        risk_level = "MEDIUM RISK"
    else:
        risk_level = "WATCH"

    # Human-readable explanation ("Why This Looks Suspicious")
    if risk_level == "HIGH RISK":
        explanation = (
            f"This message exhibits critical warning signs commonly found in {category.lower()} campaigns. "
            f"It pairs artificial urgency with threats or immediate payment demands to bypass rational verification."
        )
    elif risk_level == "MEDIUM RISK":
        explanation = (
            f"This message displays suspicious elements consistent with unverified solicitations or potential phishing. "
            f"Independent verification is strongly recommended before replying or sharing any data."
        )
    else:
        explanation = (
            "Few typical scam patterns were detected in this message. However, always exercise caution "
            "with unexpected communications or unknown senders."
        )

    # Detailed synthesis of red flags
    detailed_findings = []
    for rf in matched_red_flags:
        snippets_str = ", ".join([f"'{s}'" for s in rf["detected_snippets"]])
        detailed_findings.append(f"{rf['name']}: Detected trigger words ({snippets_str}). {rf['description']}")

    recommendations = generate_recommendations(category, rf_ids)

    return {
        "success": True,
        "input_preview": clean_text[:120] + ("..." if len(clean_text) > 120 else ""),
        "category": category,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "red_flags": matched_red_flags,
        "detailed_findings": detailed_findings,
        "why_suspicious": explanation,
        "recommended_actions": recommendations,
        "assessment_disclaimer": "AI assessment — not guaranteed truth.",
        "model_info": "ScamRadar Local Rule-Based NLP Engine (Deterministic & Explainable)"
    }


if __name__ == "__main__":
    # Self-test with sample electricity scam
    sample = "Your electricity connection will be disconnected today. Pay ₹2,500 immediately using the following link to avoid service interruption."
    res = analyze_message(sample)
    print("--- SELF TEST ---")
    print(f"Category: {res['category']}")
    print(f"Risk Level: {res['risk_level']} ({res['risk_score']}/100)")
    print(f"Red Flags: {[rf['name'] for rf in res['red_flags']]}")
    print(f"Why Suspicious: {res['why_suspicious']}")
    print(f"Recommendations: {len(res['recommended_actions'])} actions")
