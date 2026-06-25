"""Simple RAG implementation using in-memory vector store and Gemini embeddings."""

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import get_settings

SYNTHETIC_DATA = [
    "Our Comprehensive policy covers both at-fault accidents and natural disasters, including floods and earthquakes.",
    "The Third Party policy only covers damages to other people's property or vehicles when you are at fault.",
    "You can add a Rent-a-Car addon to any policy to get a temporary vehicle while yours is in the shop.",
    "To file a claim, you must provide your policy number and details of the incident. An adjuster will review it within 48 hours.",
    "Claims can take up to 7 business days to process after all documentation is submitted.",
    "If your vehicle is totaled, we will pay out the current market value of the car at the time of the accident.",
    "Premium payments are due annually. We do not offer monthly installment plans at this time.",
    "Windshield replacements are covered under the Comprehensive plan without a deductible.",
    "You can cancel your policy at any time, but refunds are pro-rated based on the remaining months minus a $50 cancellation fee."
]

def get_retriever():
    settings = get_settings()
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.google_api_key
    )
    docs = [Document(page_content=text) for text in SYNTHETIC_DATA]
    vectorstore = InMemoryVectorStore.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 2})

_retriever = None

def search_insurance_knowledge(query: str) -> str:
    """Search the insurance knowledge base for policy details, rules, or FAQs."""
    global _retriever
    if _retriever is None:
        _retriever = get_retriever()
    
    results = _retriever.invoke(query)
    if not results:
        return "No relevant information found in the knowledge base."
    
    return "\n".join([f"- {doc.page_content}" for doc in results])
