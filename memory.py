def get_transcript(messages, max_turns=6):
    """
    Returns a formatted string of the last `max_turns` exchanges.
    """
    if not messages:
        return "No prior conversation history."
        
    transcript = []
    # Take the last max_turns * 2 messages (to include both user and agent)
    for msg in messages[-(max_turns * 2):]:
        role = "User" if msg["role"] == "user" else "Agent"
        content = msg["content"]
        transcript.append(f"{role}: {content}")
        
    return "\n".join(transcript)
