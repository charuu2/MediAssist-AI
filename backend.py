# backend.py
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Globals for lazy loading
_vectorstore = None
_rag_chain = None

def load_vectorstore_and_chain():
    global _vectorstore, _rag_chain
    if _vectorstore is None or _rag_chain is None:
        # Load PDFs
        loader = DirectoryLoader("Data/", glob="*.pdf", loader_cls=PyPDFLoader)
        extracted_data = loader.load()

        # Split text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_chunks = text_splitter.split_documents(extracted_data)

        # Embeddings + vectorstore
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        _vectorstore = FAISS.from_documents(text_chunks, embeddings)
        retriever = _vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":3})

        # LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.2,
            max_output_tokens=300
        )

        # RAG chain
        system_prompt = """You are a helpful medical assistant.
Use the following context to answer concisely.
If you don’t know, say 'I don’t know'. 
Maximum 3 sentences.

{context}"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        qa_chain = create_stuff_documents_chain(llm, prompt)
        _rag_chain = create_retrieval_chain(retriever, qa_chain)

    return _rag_chain

def ask_question(query: str):
    rag_chain = load_vectorstore_and_chain()  # Lazy-load on first request
    response = rag_chain.invoke({"input": query})
    answer = response.get("answer", "I don't know")
    sources = []
    if "context" in response:
        for doc in response["context"]:
            sources.append(doc.metadata.get("source", "Unknown source"))
    return answer, sources
