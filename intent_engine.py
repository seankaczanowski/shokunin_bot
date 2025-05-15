from seasonal_wisdom import get_market_session

def evaluate_ichimoku_flow(weather, session_context):
    flow_state = {}
    score = 0
    comment_parts = []

    sky = weather.get("sky", "")
    wind = weather.get("wind", "")
    cloud = weather.get("cloud", "")
    freedom = weather.get("freedom", "")
    momentum = weather.get("momentum", "")

    if sky == "Clear skies":
        score += 1
        comment_parts.append("Clear skies signal upward openness.")
    elif sky == "Stormy":
        score -= 1
        comment_parts.append("Storm clouds dim the outlook.")

    if wind == "Favorable tailwinds":
        score += 1
        comment_parts.append("Tailwinds support bullish action.")
    elif wind == "Unfavorable headwinds":
        score -= 1
        comment_parts.append("Headwinds push against progress.")

    if momentum == "Quick favorable winds":
        score += 1
        comment_parts.append("Momentum is swift and strong.")
    elif momentum == "Slack and sluggish sails":
        score -= 1
        comment_parts.append("Momentum is weak and uncertain.")

    if freedom == "Path is clear above":
        score += 1
        comment_parts.append("Open sky for bullish movement.")
    elif freedom == "Path is clear below":
        score -= 1
        comment_parts.append("Bearish air is unblocked.")

    if cloud == "Thick and stable cloud":
        comment_parts.append("Thick cloud can act as support or resistance.")

    if score >= 3:
        bias = "bullish"
        confidence = "strong"
    elif score == 2:
        bias = "bullish"
        confidence = "moderate"
    elif score == 1:
        bias = "bullish"
        confidence = "low"
    elif score == 0:
        bias = "neutral"
        confidence = "low"
    elif score == -1:
        bias = "bearish"
        confidence = "low"
    elif score == -2:
        bias = "bearish"
        confidence = "moderate"
    else:
        bias = "bearish"
        confidence = "strong"

    if session_context["session"] in ["Weekend", "Holiday", "Friday Close"]:
        return {
            "bias": "avoid",
            "confidence": "low",
            "comment": f"{session_context['notes']} Avoid trading during {session_context['session']}.",
            "score": score,
            "session": session_context["session"],
            "session_mood": session_context["mood"],
            "volatility": session_context["volatility"],
            "session_notes": session_context["notes"]
        }

    return {
        "bias": bias,
        "confidence": confidence,
        "comment": " ".join(comment_parts) + f" Session: {session_context['session']} ({session_context['mood']})",
        "score": score,
        "session": session_context["session"],
        "session_mood": session_context["mood"],
        "volatility": session_context["volatility"],
        "session_notes": session_context["notes"]
    }

def interpret_weather(weather):
    session_context = get_market_session()
    return evaluate_ichimoku_flow(weather, session_context)