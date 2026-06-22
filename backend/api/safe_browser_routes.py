from flask import Blueprint, jsonify, request
import re, time, hashlib, numpy as np
from collections import defaultdict, deque
import math

from backend.security.google_safe_browsing import check_url_safety
from backend.security.phishing_detector import detect_phishing
from backend.security.ai_scam_detector import detect_scam

safe_browser_bp = Blueprint("safe_browser", __name__)


# =====================================================
# 🌐 CYBER SINGULARITY GLOBAL CORE
# =====================================================
class CyberSingularityCore:

    def __init__(self):

        self.blacklist = {
            "fake-login.com",
            "crypto-hack.io",
            "bank-secure-verify.com",
            "secure-bank-update.net",
            "quantum-phish.net",
            "zero-day-exploit.net"
        }

        # 🧠 long-term memory (domain intelligence)
        self.memory = defaultdict(lambda: deque(maxlen=100))

        # 🌍 global threat intelligence field
        self.global_risk = defaultdict(float)

        # ⚡ behavioral attack clusters
        self.attack_graph = defaultdict(list)

        # 🧬 trust system (self-adjusting)
        self.trust = defaultdict(lambda: 70)

        # 💾 ultra cache (stable safe predictions only)
        self.cache = {}

    # =========================
    # DOMAIN EXTRACTION
    # =========================
    def domain(self, url):
        return url.replace("https://", "").replace("http://", "").split("/")[0]

    # =========================
    # BLACKLIST CORE
    # =========================
    def is_blacklisted(self, url):
        return self.domain(url) in self.blacklist

    # =========================
    # ATTACK CLUSTER LEARNING
    # =========================
    def learn(self, url, score, dna):

        pattern = re.sub(r"\d+", "", url.lower())

        self.attack_graph[pattern].append({
            "score": score,
            "entropy": dna["entropy"],
            "tokens": dna["suspicious_tokens"]
        })

        self.global_risk[pattern] = np.mean(
            [x["score"] for x in self.attack_graph[pattern]]
        )

    # =========================
    # TRUST EVOLUTION
    # =========================
    def update_trust(self, url, score):

        d = self.domain(url)

        if score < 50:
            self.trust[d] -= 5
        else:
            self.trust[d] += 2

        self.trust[d] = max(0, min(100, self.trust[d]))
        self.memory[d].append(score)

    # =========================
    # RISK DRIFT (BEHAVIOR SHIFT DETECTION)
    # =========================
    def drift(self, url):

        d = self.domain(url)
        h = self.memory[d]

        if len(h) < 10:
            return 0

        return abs(np.mean(list(h)[-10:]) - np.mean(list(h)[:10]))

    # =========================
    # CACHE (ONLY HIGH CONFIDENCE)
    # =========================
    def cache_get(self, url):
        return self.cache.get(hashlib.md5(url.encode()).hexdigest())

    def cache_set(self, url, data):
        if data.get("confidence", 0) > 95:
            self.cache[hashlib.md5(url.encode()).hexdigest()] = data


core = CyberSingularityCore()


# =====================================================
# 🧬 FINAL DNA ENGINE
# =====================================================
class DNAEngine:

    def scan(self, url):

        return {
            "length": len(url),
            "digits": sum(c.isdigit() for c in url),
            "entropy": len(set(url)) / max(len(url), 1),
            "specials": len(re.findall(r"[^a-zA-Z0-9]", url)),
            "has_ip": bool(re.search(r"\d+\.\d+\.\d+\.\d+", url)),
            "subdomains": url.count("."),
            "tokens": len(re.findall(
                r"(login|verify|secure|bank|otp|password|wallet|account|signin|auth)",
                url.lower()
            )),
            "complexity": len(re.findall(r"[?&=]", url))
        }


dna_engine = DNAEngine()


# =====================================================
# 🧠 FINAL AI BRAIN (ENSEMBLE DECISION CORE)
# =====================================================
class FinalAIBrain:

    def evaluate(self, dna, trust, drift, risk):

        score = 100
        reasons = []

        if dna["entropy"] < 0.4:
            score -= 25
            reasons.append("entropy anomaly")

        if dna["has_ip"]:
            score -= 50
            reasons.append("IP impersonation")

        if dna["tokens"] > 2:
            score -= 30
            reasons.append("credential attack pattern")

        if dna["complexity"] > 10:
            score -= 20
            reasons.append("URL obfuscation")

        score -= drift * 0.8
        score -= risk * 0.5

        score *= (1.6 - trust / 100)

        return max(0, score), reasons


ai = FinalAIBrain()


# =====================================================
# ⚖️ FINAL FUSION ENGINE (REAL AI STYLE WEIGHTING)
# =====================================================
class FusionCore:

    def fuse(self, scores):

        values = np.array(list(scores.values()))

        weights = np.array([0.35, 0.25, 0.15, 0.15, 0.10])

        return float(np.dot(values, weights))


fusion = FusionCore()


# =====================================================
# 🧠 FINAL CYBER JUDGE (UNCERTAINTY MODEL)
# =====================================================
class Judge:

    def decide(self, scores):

        mean = np.mean(list(scores.values()))
        var = np.var(list(scores.values()))

        risk = 1 / (1 + math.exp(-(60 - mean) / 7))

        if risk < 0.2 and var < 25:
            return "BENIGN"
        elif risk < 0.5:
            return "SUSPICIOUS"
        elif risk < 0.8:
            return "MALICIOUS"
        else:
            return "CRITICAL_THREAT"


judge = Judge()


# =====================================================
# 🚀 FINAL SCANNER CORE (LEVEL 20)
# =====================================================
@safe_browser_bp.route("/scan", methods=["POST"])
def scan_url():

    start = time.time()
    url = (request.json or {}).get("url", "").strip()

    if not url:
        return jsonify({"error": "URL required"}), 400

    # =========================
    # BLACKLIST
    # =========================
    if core.is_blacklisted(url):
        return jsonify({
            "url": url,
            "safe": False,
            "status": "QUARANTINED",
            "intent": "CRITICAL_THREAT",
            "score": 0,
            "confidence": 100,
            "reasons": ["GLOBAL BLOCKLIST MATCH"],
            "scan_time_ms": round((time.time() - start) * 1000, 2)
        })

    # =========================
    # CACHE
    # =========================
    cached = core.cache_get(url)
    if cached:
        cached["cached"] = True
        return jsonify(cached)

    # =========================
    # ANALYSIS PIPELINE
    # =========================
    dna = dna_engine.scan(url)

    d = core.domain(url)
    trust = core.trust[d]
    drift = core.drift(url)
    risk = core.global_risk.get(url, 0)

    ai_score, ai_reasons = ai.evaluate(dna, trust, drift, risk)

    try:
        google = check_url_safety(url)
    except:
        google = {"safe": True, "threats": []}

    phishing = detect_phishing(url)
    scam = detect_scam(url)

    ml_score = max(50, 90 - dna["entropy"] * 50)

    # =========================
    # SCORE SPACE
    # =========================
    scores = {
        "ai": ai_score,
        "ml": ml_score,
        "google": 100 if google.get("safe", True) else 5,
        "dna": 100 - (70 * (1 - dna["entropy"])),
        "graph": 100 - drift
    }

    final_score = fusion.fuse(scores)

    intent = judge.decide(scores)

    safe = (intent == "BENIGN" and final_score > 95)

    status = (
        "SAFE" if safe else
        "RISK" if final_score > 75 else
        "DANGEROUS" if final_score > 50 else
        "QUARANTINED"
    )

    # =========================
    # REASON ENGINE
    # =========================
    reasons = ai_reasons
    if phishing:
        reasons.append("phishing detected")
    if scam:
        reasons.append("scam detected")

    reasons += google.get("threats", [])
    reasons = list(dict.fromkeys(reasons))

    # =========================
    # LEARNING LOOP
    # =========================
    core.update_trust(url, final_score)
    core.learn(url, final_score, dna)

    # =========================
    # CONFIDENCE (REALISTIC MODEL)
    # =========================
    confidence = 100 - abs(50 - final_score) * 0.9
    confidence = max(0, min(100, confidence))

    # =========================
    # RESPONSE
    # =========================
    response = {
        "url": url,
        "safe": safe,
        "status": status,
        "intent": intent,
        "score": round(final_score, 2),
        "confidence": round(confidence, 2),
        "dna": dna,
        "scores": scores,
        "drift": drift,
        "reasons": reasons,
        "scan_time_ms": round((time.time() - start) * 1000, 2)
    }

    core.cache_set(url, response)

    return jsonify(response)
