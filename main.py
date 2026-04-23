from dotenv import load_dotenv
from rag import load_documents, create_vectorstore, get_retriever, ask_rag, fallback_response
from intent import classify_intent
from lead_flow import handle_lead
from state import AppState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# RAG setup
docs = load_documents()
vs = create_vectorstore(docs)
retriever = get_retriever(vs)

def classifier_node(state: AppState):
    user_input = state["messages"][-1]["content"] if state.get("messages") else ""
    intent = classify_intent(user_input, state.get("messages", []), state.get("stage"))
    return {"intent": intent}

def router(state: AppState):
    intent = state.get("intent")
    stage = state.get("stage")
    
    if stage:
        if intent == "inquiry":
            return "rag"
        elif intent == "exit":
            return "exit_lead"
        else: # Either providing details or something else - proceed to lead_flow for handling
            return "lead_flow"
    else:
        if intent == "greeting":
            return "greeting"
        elif intent == "inquiry":
            return "rag"
        elif intent in ("high_intent", "update_details"):
            return "lead_flow"
        elif intent == "exit":
            return "exit_lead"
        else:
            return "other"

def greeting_node(state: AppState):
    response = "Hello! I'm the AutoStream assistant. How can I help you today?"
    return {"messages": [{"role": "agent", "content": response}]}

def rag_node(state: AppState):
    user_input = state["messages"][-1]["content"] if state.get("messages") else ""
    response = ask_rag(retriever, user_input, state.get("messages", []))
    
    # If interrupted during lead flow, softly bring them back
    if state.get("stage"):
        response += "\n\nShall we continue with your signup?"
        
    return {"messages": [{"role": "agent", "content": response}]}

def lead_node(state: AppState):
    user_input = state["messages"][-1]["content"] if state.get("messages") else ""
    
    # Initialize user_data if not present
    user_data = dict(state.get("user_data", {}))
    if not user_data or "name" not in user_data:
        user_data = {"name": None, "email": None, "platform": None}
        
    state_copy = {"stage": state.get("stage"), "user_data": user_data, "messages": state.get("messages", []), "intent": state.get("intent")}
    
    reply = handle_lead(state_copy, user_input)
        
    return {"messages": [{"role": "agent", "content": reply}], "stage": state_copy["stage"], "user_data": state_copy["user_data"]}

def exit_lead_node(state: AppState):
    reply = "Goodbye, Thank you for your time and patience."
    return {
        "messages": [{"role": "agent", "content": reply}], 
        "stage": None, 
        "user_data": {"name": None, "email": None, "platform": None}
    }

def other_node(state: AppState):
    user_input = state["messages"][-1]["content"] if state.get("messages") else ""
    response = fallback_response(user_input, state.get("messages", []))
    return {"messages": [{"role": "agent", "content": response}]}

# Build Graph
builder = StateGraph(AppState)
builder.add_node("classifier", classifier_node)
builder.add_node("greeting", greeting_node)
builder.add_node("rag", rag_node)
builder.add_node("lead_flow", lead_node)
builder.add_node("exit_lead", exit_lead_node)
builder.add_node("other", other_node)

builder.add_edge(START, "classifier")
builder.add_conditional_edges("classifier", router)
builder.add_edge("greeting", END)
builder.add_edge("rag", END)
builder.add_edge("lead_flow", END)
builder.add_edge("exit_lead", END)
builder.add_edge("other", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print("Agent ready. Type 'exit' to stop.\n")
    thread_config = {"configurable": {"thread_id": "user_1"}}
    
    # Initialize state explicitly
    graph.update_state(thread_config, {"stage": None, "user_data": {"name": None, "email": None, "platform": None}})
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Agent: Goodbye!")
            break
            
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        
        output = None
        for step in graph.stream(inputs, config=thread_config, stream_mode="values"):
            output = step
            
        if output and output.get("messages"):
            print("Agent:", output["messages"][-1]["content"])