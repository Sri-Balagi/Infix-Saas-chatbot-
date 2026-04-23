import os
from main import graph
import time

conversations = [
    # 1. Happy Path Lead Capture
    ["Hi", "I want to sign up", "Alice", "alice@example.com", "YouTube"],
    
    # 2. Inquiry first, then lead capture
    ["Hello, what is your pricing?", "That sounds good, I'd like to sign up", "Bob", "bob@example.com", "Instagram"],
    
    # 3. Interruption during lead capture
    ["Sign me up!", "Charlie", "Wait, what are the features of the Pro plan?", "charlie@sample.com", "TikTok"],
    
    # 4. Out of scope then signup
    ["Who is the CEO of AutoStream?", "Nevermind, I want to subscribe", "Diana", "diana@test.com", "Twitch"],
    
    # 5. Over-sharing in one prompt (testing extraction)
    ["Hi there", "Please get me started, my name is Edward.", "My email is edward@gmail.com", "I am a content creator on Vimeo."],
    
    # 6. Giving wrong data format (testing fallback/reprompt)
    ["I want to sign up", "My name is Fiona", "I don't have an email", "fiona@fiona.com", "YouTube"],
    
    # 7. Unrelated interruption
    ["Sign me up", "George", "How to bake a cake?", "george@george.com", "Instagram"],
    
    # 8. Complete cancellation midway
    ["I'd like to sign up", "Harry", "Actually, I changed my mind.", "exit"],
    
    # 9. Simple inquiries
    ["Hello there", "Do you offer refunds?", "Okay, thanks. Bye", "exit"],
    
    # 10. Natural conversational flow
    ["Hey, tell me about your service", "Interesting, do you have any annual plans?", "I'll take the Pro plan then", "It's Jack", "jack@youtube.com", "YouTube"]
]

def run_tests():
    with open("test_results2.txt", "w", encoding="utf-8") as f:
        for idx, sequence in enumerate(conversations):
            f.write(f"=== TEST CONVERSATION {idx + 1} ===\n")
            thread_config = {"configurable": {"thread_id": f"test_user_{idx}"}}
            
            # Initialize explicitly
            graph.update_state(thread_config, {"stage": None, "user_data": {"name": None, "email": None, "platform": None}})
            
            for msg in sequence:
                f.write(f"USER: {msg}\n")
                
                inputs = {"messages": [{"role": "user", "content": msg}]}
                output = None
                
                try:
                    for step in graph.stream(inputs, config=thread_config, stream_mode="values"):
                        output = step
                except Exception as e:
                    f.write(f"AGENT CRASHED: {e}\n")
                    break
                    
                if output and output.get("messages"):
                    f.write(f"AGENT: {output['messages'][-1]['content']}\n")
                
                # Check lead variables
                if output and output.get("user_data"):
                    f.write(f"   [STATE DATA: {output['user_data']}]\n")
                    
                # To prevent overloading free tier APIs, wait dynamically:
                time.sleep(3)
                
            f.write("=== END THREAD ===\n\n")

if __name__ == "__main__":
    print("Running sequence of 10 simulated conversations...")
    print("Pausing between API calls to respect OpenRouter Free Tier limits.")
    run_tests()
    print("Done! Check test_results.txt")
