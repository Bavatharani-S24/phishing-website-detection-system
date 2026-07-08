from models.phishing_model import PhishingDetector

class EmailAnalyzer:
    def __init__(self):
        self.detector = PhishingDetector()

    def analyze_email(self, text):
        reasons = []
        score = self.detector.predict(text)

        if "urgent" in text.lower():
            reasons.append("Urgent language detected")
        if "click" in text.lower():
            reasons.append("Suspicious call-to-action")

        return {
            "risk_score": score,
            "reasons": reasons
        }