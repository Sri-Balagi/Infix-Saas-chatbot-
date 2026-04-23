from tools import mock_lead_capture
from rag import extract_entity
from memory import get_transcript

def handle_lead(state, user_input):
    user_data = state["user_data"]
    stage = state["stage"]
    history = get_transcript(state["messages"])
    
    if user_input:
        lower_check = user_input.lower()
        if "change my name" in lower_check or "wrong name" in lower_check or ("change" in lower_check and "name" in lower_check):
            user_data["name"] = None
            state["stage"] = "ask_name"
            return "Not a problem! What would you like to update your name to?"
        elif "change my email" in lower_check or "wrong email" in lower_check or ("change" in lower_check and "email" in lower_check):
            user_data["email"] = None
            state["stage"] = "ask_email"
            return "Got it. What would you like to update your email address to?"
        elif "change my platform" in lower_check or "wrong platform" in lower_check or ("change" in lower_check and "platform" in lower_check) or "platform list" in lower_check:
            user_data["platform"] = None
            state["stage"] = "ask_platform"
            return "No worries! Please select or type your updated platform(s)."
        
    # Actually extract the data if we just asked for it and user provided details
    if user_input:
        lower_input = user_input.lower()
        
        # Out-of-order corrections
        if "name is" in lower_input or "name:" in lower_input or "call me" in lower_input:
            extracted = extract_entity("Name", user_input, history)
            if extracted: user_data["name"] = extracted
        if "email is" in lower_input or "email:" in lower_input or "@" in lower_input:
            extracted = extract_entity("Email Address", user_input, history)
            if extracted: user_data["email"] = extracted
        if "platform is" in lower_input or "use" in lower_input or "create on" in lower_input:
            extracted = extract_entity("Platform", user_input, history)
            if extracted and "other" not in extracted.lower(): user_data["platform"] = extracted
            
        # Standard stage-gated extraction
        if (stage == "ask_name" or not stage) and not user_data["name"]:
            extracted = extract_entity("Name", user_input, history)
            if extracted: user_data["name"] = extracted
        elif stage == "ask_email" and not user_data["email"]:
            extracted = extract_entity("Email Address", user_input, history)
            if extracted: user_data["email"] = extracted
        elif stage == "ask_platform" and not user_data["platform"]:
            if lower_input == "other" or "other ✍️" in lower_input:
                return "Got it! Please type the name of the social media platform you primarily use."
            # Multi-platform input from UI buttons comes as comma-separated clean text — store directly
            if "," in user_input or any(p in user_input for p in ["YouTube","Instagram","TikTok","Facebook","LinkedIn","Twitch","Snapchat","Pinterest","Reddit","Threads","Kwai","Likee","ShareChat","Moj","Josh","Chingari"]):
                user_data["platform"] = user_input.strip()
            else:
                extracted = extract_entity("Platform", user_input, history)
                if extracted and "other" not in extracted.lower():
                    user_data["platform"] = extracted

    # Determine what to ask next based on missing data
    if not user_data["name"]:
        state["stage"] = "ask_name"
        if user_input and stage == "ask_name":
            return "Please provide a valid, authentic human name so we can properly set up your account."
        return "Could I have your full name?"
    elif not user_data["email"]:
        state["stage"] = "ask_email"
        # Explicitly address users resisting email collection
        if user_input and ("don't have" in user_input.lower() or "no email" in user_input.lower() or "don't want" in user_input.lower()):
            return "An email ID is required in order to avail this service and to get in touch with the service provider."
            
        short_name = user_data["name"].split()[0] if user_data["name"] else "there"
        return f"Nice to meet you, {short_name}! What's your email address?"
    elif not user_data["platform"]:
        state["stage"] = "ask_platform"
        return "Awesome. Finally, which platform do you primarily create content on?"
    else:
        # All data collected
        mock_lead_capture(
            user_data["name"],
            user_data["email"],
            user_data["platform"]
        )
        state["stage"] = None # Reset stage after successful capture
        return "Thanks! We've successfully captured your details. Our team will get in touch soon, or you can check your email for the next steps!"