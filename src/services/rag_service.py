"""
RAG Service - Pure Qdrant-based chatbot
Search textbook, return relevant sections. Simple. Clean. No bloat.
"""
import os
from typing import List, Optional, Tuple
import os
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from src.core.config import settings

# Global state
_qdrant_client = None
_embedding_model = None

# Optional: LLM agent for human-style answers
_llm_agent = None


def _get_llm_agent():
    """
    Lazy-init OpenAI 'Agent' (via openai-agents) to rewrite RAG chunks
    into short, human-style answers.
    """
    global _llm_agent
    if _llm_agent is not None:
        return _llm_agent

    try:
        from agents import Agent  # type: ignore

        if not settings.OPENAI_API_KEY:
            print("[RAG] OPENAI_API_KEY not set; running in pure-RAG mode")
            return None

        # Ensure env var is set for openai-agents
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

        _llm_agent = Agent(
            name="RAG Answer Rewriter",
            instructions=(
                "You are a specialized AI assistant and expert tutor for the 'Physical AI & Humanoid Robotics' textbook. "
                "Your primary goal is to help users understand the book's content by providing clear, concise, and friendly explanations.\n\n"
                "**Core Persona:**\n"
                "- **Friendly Tutor:** Act as a patient, encouraging, and knowledgeable guide.\n"
                "- **Expert:** You have a deep understanding of all topics covered in the book, including ROS2, Isaac Sim, digital twins, and general robotics concepts.\n"
                "- **Focused:** Your knowledge is strictly limited to the content of this textbook.\n\n"
                "**Rules of Engagement:**\n\n"
                "1.  **Scope of Knowledge:**\n"
                "    - **DO:** Only answer questions that can be answered using the content of the 'Physical AI & Humanoid Robotics' textbook. All your responses must be grounded in the provided textbook excerpts (context).\n"
                "    - **DO NOT:** Answer questions about any other topic, book, or general knowledge. If a user asks an out-of-scope question (e.g., about politics, movies, or another technical subject), politely decline and steer the conversation back to the textbook. For example, say: \"My expertise is limited to the 'Physical AI & Humanoid Robotics' textbook. I can help you with topics like ROS2, digital twins, or any other concept from the book.\"\n\n"
                "2.  **Language and Communication:**\n"
                "    - **DO:** Detect the user's language and respond in the **same language**. If the user asks a question in Urdu, you must provide the full answer in Urdu. If they ask in English, answer in English.\n"
                "    - **DO:** Maintain a conversational, natural, and easy-to-understand tone. Avoid overly technical jargon unless it's a specific term from the book that you are explaining.\n"
                "    - **DO:** Write short, clear, human-like answers. Aim for 2-5 sentences for most explanations to keep it digestible.\n"
                "    - **DO NOT:** Use raw markdown, code snippets, or file headings from the source material in your answer. Explain the concepts in your own words.\n\n"
                "3.  **Answering and Explanation Flow:**\n"
                "    - **DO:** When a user asks a question, use the provided context from the textbook to formulate your answer.\n"
                "    - **DO:** If the user expresses confusion or asks for clarification (e.g., \"I don't understand,\" \"explain again,\" \"what does that mean?\"), re-explain the concept in even simpler terms. Maintain the same language they are using.\n"
                "    - **DO:** If the provided context is insufficient to answer the question, state that you couldn't find specific information on that topic within the textbook.\n\n"
                "4.  **Greeting:**\n"
                "    - **DO:** If the user starts with a simple greeting (e.g., \"Hi\", \"Hello\", \"Salam\"), respond with a welcoming message that introduces yourself and your purpose. For example: \"Hi! I'm your AI assistant for the 'Physical AI & Humanoid Robotics' textbook. How can I help you with ROS2, Isaac Sim, or other robotics topics from the book today?\""
            ),
            model="gpt-4o-mini",
        )
        print("[OK] LLM agent initialized for RAG answers")
        return _llm_agent
    except Exception as e:
        print(f"[WARN] Could not initialize LLM agent, falling back to raw RAG text: {e}")
        return None

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")


def _get_qdrant():
    """Initialize Qdrant client once"""
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client
    
    try:
        if settings.QDRANT_URL:
            print("[RAG] Initializing Qdrant Cloud client...")
            _qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=10.0,
                prefer_grpc=False,
                check_compatibility=False,
            )
            print("[OK] Qdrant Cloud connected")
        else:
            print("[RAG] Initializing local Qdrant client...")
            _qdrant_client = QdrantClient(
                host=os.getenv("QDRANT_HOST", "localhost"),
                port=int(os.getenv("QDRANT_PORT", "6333")),
                timeout=10.0,
            )
            print("[OK] Local Qdrant connected")
        return _qdrant_client
    except Exception as e:
        print(f"[ERROR] Qdrant error: {e}")
        raise


def _get_embedder():
    """Initialize embedding model once"""
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    
    try:
        print("[RAG] Loading FastEmbed model (BAAI/bge-small-en-v1.5)...")
        _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        print("[OK] Embedder loaded")
        return _embedding_model
    except Exception as e:
        print(f"[ERROR] Embedder error: {e}")
        raise


class RAGService:
    """Pure RAG Service - Search Qdrant, return results"""
    
    def __init__(self):
        self.qdrant = _get_qdrant()
        self.embedder = _get_embedder()
    
    async def generate_response(
        self,
        query: str,
        selected_text: Optional[str] = None,
        current_page: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
        limit: int = 3
    ) -> dict:
        """
        Direct LLM Chatbot - No RAG, No Qdrant.
        Just passes the query (and history) to the OpenAI Agent.
        """
        try:
            print("[RAG] generate_response() start - DIRECT LLM MODE")
            print(f"[RAG] Raw query: {query!r}")

            # 1. Get the Agent
            agent = _get_llm_agent()
            if not agent:
                return {
                    "answer": "LLM Agent not initialized. Please check OPENAI_API_KEY.",
                    "sources": [],
                    "search_used": "error"
                }

            from agents import Runner  # type: ignore

            # 2. Build Prompt
            # We include conversation history and the current query.
            # We also include selected_text if present, as context.
            
            history_text = ""
            if conversation_history:
                last_msgs = conversation_history[-6:] # Keep last 6 messages
                parts = []
                for m in last_msgs:
                    role = m.get("role", "user")
                    prefix = "User" if role == "user" else "Assistant"
                    parts.append(f"{prefix}: {m.get('content', '')}")
                history_text = "\n".join(parts)

            context_instruction = ""
            if selected_text:
                context_instruction = f"\n\nUser selected text:\n'''{selected_text}'''\n\nPlease explain or answer based on this text."

            prompt = (
                f"Conversation History:\n{history_text}\n\n"
                f"User: {query}"
                f"{context_instruction}\n\n"
                "Assistant:"
            )

            # 3. Run Agent
            print("[RAG] Calling LLM...")
            # Use await as per translator.py pattern
            llm_answer = await Runner.run(agent, input=prompt)
            
            # Extract text from RunResult
            final_answer = ""
            if hasattr(llm_answer, 'final_output'):
                 final_answer = str(llm_answer.final_output)
            elif hasattr(llm_answer, 'output'):
                 final_answer = str(llm_answer.output)
            elif hasattr(llm_answer, 'content'):
                 final_answer = str(llm_answer.content)
            elif isinstance(llm_answer, str):
                 final_answer = llm_answer
            else:
                 # Fallback: try to parse string if it looks like RunResult
                 raw_str = str(llm_answer)
                 if "Final output (str):" in raw_str:
                     try:
                         # Hacky parsing if attribute access fails
                         part = raw_str.split("Final output (str):")[1]
                         # It might be followed by " - " or end of string
                         if " - " in part:
                             final_answer = part.split(" - ")[0].strip()
                         else:
                             final_answer = part.strip()
                     except:
                         final_answer = raw_str
                 else:
                     final_answer = raw_str

            return {
                "answer": final_answer,
                "sources": [], # No sources since no RAG
                "search_used": "direct_llm",
            }

        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            print(f"[ERROR] LLM error: {type(e).__name__}: {e}\n{trace}")
            return {
                "answer": f"Error: {type(e).__name__}: {str(e)}",
                "sources": [],
                "search_used": "error",
            }


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
