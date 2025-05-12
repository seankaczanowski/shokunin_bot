# intent_engine.py
# Gentle guidance from the Ichimoku weather

def interpret_weather(weather):
    """
    Soft interpretation of Ichimoku weather into trading bias and confidence.
    """

    sky = weather.get("sky", "")
    cloud = weather.get("cloud", "")
    wind = weather.get("wind", "")
    freedom = weather.get("freedom", "")
    momentum = weather.get("momentum", "")

    score = 0
    comment_parts = []

    # === BULLISH SIGNALS ===
    if sky == "Clear skies":
        score += 1
        comment_parts.append("Sky is clear and welcoming.")
    if wind == "Favorable tailwinds":
        score += 1
        comment_parts.append("Tailwinds support upward movement.")
    if momentum == "Quick favorable winds":
        score += 1
        comment_parts.append("Momentum is gaining strength.")
    if freedom == "Path is clear above":
        score += 1
        comment_parts.append("The path above is open.")
    if cloud == "Thick and stable cloud":
        score += 1
        comment_parts.append("Cloud base is solid, offering support.")

    if score >= 3:
        return {
            "bias": "bullish",
            "confidence": "moderate" if score == 3 else "strong",
            "comment": " ".join(comment_parts),
            "score": score
        }

    # === BEARISH SIGNALS ===
    score = 0
    comment_parts = []

    if sky == "Stormy":
        score += 1
        comment_parts.append("The sky is stormy and dark.")
    if wind == "Unfavorable headwinds":
        score += 1
        comment_parts.append("Headwinds resist upward motion.")
    if momentum == "Slack and sluggish sails":
        score += 1
        comment_parts.append("Momentum is fading.")
    if freedom == "Path is clear below":
        score += 1
        comment_parts.append("The path below is wide open.")
    if cloud == "Thick and stable cloud":
        score += 1
        comment_parts.append("Cloud hangs heavy overhead.")

    if score >= 3:
        return {
            "bias": "bearish",
            "confidence": "moderate" if score == 3 else "strong",
            "comment": " ".join(comment_parts),
            "score": score
        }

    # === MIXED OR UNCLEAR ===
    unclear = [sky, wind, momentum, freedom, cloud].count("Unknown wind") + \
              [sky, wind, momentum, freedom, cloud].count("Unknown path") + \
              [sky, wind, momentum, freedom, cloud].count("Unknown momentum")

    if unclear >= 3:
        return {
            "bias": "avoid",
            "confidence": "low",
            "comment": "Too many unknowns to act decisively.",
            "score": 0
        }

    if cloud == "Thin and fragile cloud" and momentum == "Quick favorable winds":
        return {
            "bias": "bullish",
            "confidence": "low",
            "comment": "Momentum is rising, but the cloud lacks substance. Proceed lightly.",
            "score": 1
        }

    return {
        "bias": "neutral",
        "confidence": "low",
        "comment": "Signals are mixed or indecisive. Stay observant.",
        "score": 0
    }
