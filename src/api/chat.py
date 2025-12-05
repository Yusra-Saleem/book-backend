from fastapi import APIRouter, Depends, HTTPException
from src.models.chat import ChatRequest, ChatResponse, Message
from src.services.rag_service import get_rag_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    import time
    start_time = time.time()
    try:
        print(f"Chat request - Query: '{request.query[:50]}...', Page: {request.current_page or 'N/A'}")
        rag_service = get_rag_service()
        
        # Convert conversation history to dict format for RAG service
        conv_history = None
        if request.conversation_history:
            conv_history = [{"role": m.role, "content": m.content} for m in request.conversation_history]
        
        result = await rag_service.generate_response(
            query=request.query,
            selected_text=request.selected_text,
            current_page=request.current_page,
            conversation_history=conv_history
        )
        
        elapsed = time.time() - start_time
        print(f"Chat response generated in {elapsed:.2f}s")
        
        # Build response with full conversation history
        new_history = []
        if request.conversation_history:
            new_history = request.conversation_history.copy()
        
        # Add user message
        new_history.append(Message(role="user", content=request.query))
        # Add assistant response
        new_history.append(Message(role="assistant", content=result['answer']))
        
        return ChatResponse(
            answer=result['answer'],
            sources=[],
            conversation_history=new_history
        )
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"Error in chat endpoint after {elapsed:.2f}s: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
