"""
AI Assistant API Endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import AIChatRequest, AIChatResponse
from app.config import settings

router = APIRouter()

@router.post("/ai/chat", response_model=AIChatResponse)
async def chat_with_ai(request: AIChatRequest):
    """
    Chat with AI assistant about ESG topics using Gemini 2.5 Flash
    """
    try:
        # Try Gemini first (primary)
        try:
            from app.services.gemini_service import GeminiESGAssistant
            assistant = GeminiESGAssistant()
            response = assistant.answer_question(request.message, request.context)
            return AIChatResponse(
                response=response,
                sources=None
            )
        except Exception as e:
            print(f"Gemini not available: {e}")
        
        # Fallback to Groq if available
        try:
            from pathlib import Path
            import sys
            backend_dir = Path(__file__).parent.parent.parent.parent
            rag_groq_path = backend_dir.parent / "rag_system_groq.py"
            if rag_groq_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("rag_system_groq", rag_groq_path)
                rag_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(rag_module)
                assistant = rag_module.ESG_RAG_Groq()
                response = assistant.answer_question(request.message, request.context)
                return AIChatResponse(
                    response=response,
                    sources=None
                )
        except Exception as e:
            print(f"Groq RAG not available: {e}")
        
        # Final fallback
        return AIChatResponse(
            response="AI assistant is currently unavailable. Please check your API keys. GEMINI_API_KEY is required.",
            sources=None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

