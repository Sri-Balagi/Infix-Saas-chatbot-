import json
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def load_documents():
    with open("data.json") as f:
        data = json.load(f)

    docs = []
    for key, value in data.items():
        docs.append(Document(page_content=f"{key}: {value}"))

    return docs


def create_vectorstore(docs):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


def get_retriever(vectorstore):
    return vectorstore.as_retriever()


def ask_rag(retriever, query, transcript=""):
    docs = retriever.invoke(query)

    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    You are a polite, helpful assistant named Infix for AutoStream (a video editing SaaS platform).

    Use the context below to answer the user's question accurately.
    The user's question might be a follow-up related to the conversation history, so use it to understand the context.
    If the context does not contain the answer, politely tell them that you can only help with AutoStream's product, pricing, and features.
    
    FORMATTING RULES (strictly follow these):
    - Do NOT use backticks or code blocks. Never use `inline code`.
    - For plan-related answers, always structure each plan like this example:
    
      **Basic Plan**
      - Price: $29/month
      - Videos per month: 10
      - Resolution: 720p
    
      **Pro Plan**
      - Price: $79/month
      - Videos: Unlimited
      - Resolution: 4K
      - AI Captions: Yes
      - Support: 24/7
    
    - For non-plan answers, write in plain friendly prose. No backticks.
    - Keep plan names bold using **Plan Name** format.
    - List features using - (dash) bullet points.

    Context:
    {context}
    
    Conversation History:
    {transcript}

    Question: {query}
    """
    response = llm_call(prompt)
    return response

def fallback_response(query, transcript=""):
    prompt = f"""
    You are a customer support assistant named Infix for AutoStream (video editing SaaS).
    The user asked something unrelated or unclear.
    
    IMPORTANT FORMATTING RULES:
    - Write in plain conversational prose only.
    - Do NOT use markdown: no backticks, no bold (**), no bullet points, no headings.
    - Keep the response brief, friendly, and consistent in font.

    Conversation History:
    {transcript}
    
    User query: {query}
    
    Politely acknowledge the user's input, briefly explain you are limited to AutoStream topics, and guide them back.
    """
    return llm_call(prompt)

def extract_entity(entity_type, user_input, history):
    prompt = f"""
    You are a strict data extractor. Extract the {entity_type} from the user's input.
    
    User input: "{user_input}"
    
    Return ONLY the extracted {entity_type}. DO NOT wrap it in quotes or add extra text.
    If the {entity_type} is NOT present in the user input, output the exact word: NONE
    
    SPECIAL RULE FOR NAME: If you are extracting a "Name", ensure it is a plausible human name or nickname. If it is clearly a joke, an AI, an object, or a fake identity (like "chatbot", "system", "nobody"), output: NONE.
    
    Examples:
    - Extracting "Name" from "My name is John Doe." -> John Doe
    - Extracting "Email" from "Wait, how much is this?" -> NONE
    - Extracting "Platform" from "I use YouTube" -> YouTube
    - Extracting "Name" from "yeah, it is chatbot" -> NONE
    """
    res = llm_call(prompt).strip().strip('"').strip("'")
    return res if res.upper() != "NONE" else None

def llm_call(prompt):
    response=client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role":"user","content":prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content