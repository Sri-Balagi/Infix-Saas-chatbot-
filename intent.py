from rag import llm_call
from memory import get_transcript

def classify_intent(user_input, messages, current_stage=None):
    transcript = get_transcript(messages)
    
    if current_stage:
        prompt = f"""
        You are an assistant currently in the active stage of capturing a lead. You just asked the user for their: {current_stage}.
        
        Conversation history:
        {transcript}
        
        Recent Input: "{user_input}"
        
        Classify the intent of the recent input into EXACTLY ONE word from the following:
        - provide_details (User is answering the question, providing requested info, confirming a step, or asking to change/correct their details)
        - inquiry (User is pausing the signup to ask a question about the product, pricing, service, or policy)
        - exit (User explicitly wants to stop, cancel, or quit the signup process)
        - other (Unrelated small talk or random input)
        """
    else:
        prompt = f"""
        You are evaluating user input for an AI assistant for AutoStream (a video editing SaaS).
        
        Conversation history:
        {transcript}
        
        Recent Input: "{user_input}"
        
        Classify the intent of the recent input into EXACTLY ONE word from the following:
        - greeting (User says hi, hello, what's up)
        - inquiry (User asks about product, pricing, service, plans, features, including follow-up questions)
        - high_intent (User wants to sign up, buy, use the product, or provide their details)
        - exit (User says bye, goodbye, exit, or wants to end the conversation)
        - other (Unrelated small talk not related to AutoStream)
        
        Output ONLY the single word classifying the intent.
        """
    
    response = llm_call(prompt)
    return response.strip().lower()
