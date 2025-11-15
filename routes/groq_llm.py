"""
Enhanced Groq LLM Service with Function Calling Support
Provides OpenAI-compatible chat completions with event planning tools
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import json
import os
import asyncio
from typing import Dict, Any, List, Union, Optional
import uuid
import time
from pydantic import BaseModel
import sys
import re

# Add parent directory to path to import event tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from event_tools import get_function_definitions, call_function, AVAILABLE_FUNCTIONS
    TOOLS_AVAILABLE = True
    print("✅ Event planning tools loaded successfully")
    print(f"📋 Available functions: {list(AVAILABLE_FUNCTIONS.keys())}")
except ImportError as e:
    TOOLS_AVAILABLE = False
    print(f"⚠️ Event planning tools not available: {e}")

router = APIRouter(prefix="/groq", tags=["groq"])

class FunctionCall(BaseModel):
    name: str
    arguments: str

class ToolCall(BaseModel):
    id: str
    type: str
    function: FunctionCall

class ChatMessage(BaseModel):
    role: str
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    stream: bool = True
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class GroqLLMService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

    async def generate_response(self, request: ChatCompletionRequest):
        """Generate response using Groq API"""
        try:
            print(f"🔧 DEBUG: Starting generate_response with model: {request.model}")
            
            # Prepare request for Groq API
            groq_request = {
                "model": request.model or self.default_model,
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "stream": request.stream,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "top_p": request.top_p,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            if request.stream:
                return self._stream_response(groq_request, headers)
            else:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=groq_request,
                        headers=headers
                    )
                    response.raise_for_status()
                    return response.json()

        except Exception as e:
            print(f"❌ DEBUG: Generate response error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Groq service error: {str(e)}")

    async def _stream_response(self, request_data: dict, headers: dict):
        """Handle streaming response from Groq API"""
        try:
            print("🔧 DEBUG: Starting stream request to Groq API")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=request_data,
                    headers=headers
                ) as response:
                    print(f"🔧 DEBUG: Stream response status: {response.status_code}")
                    response.raise_for_status()
                    
                    line_count = 0
                    async for line in response.aiter_lines():
                        line_count += 1
                        if line.strip():
                            yield f"{line}\n"
                    
                    print(f"🔧 DEBUG: Stream completed after {line_count} lines")
                    
        except Exception as e:
            print(f"❌ DEBUG: Stream error: {str(e)}")
            error_response = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request_data.get("model", "llama-3.1-8b-instant"),
                "choices": [{
                    "index": 0,
                    "delta": {"content": "I apologize, but I'm having trouble processing your request right now. Please try again."},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"

# Create service instance
groq_service = GroqLLMService()

@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        print("\n" + "="*80)
        print("🤖 GROQ LLM REQUEST RECEIVED!")
        print(f"📝 Messages count: {len(request.messages)}")
        print(f"🔧 Tools available: {TOOLS_AVAILABLE}")
        
        # Debug message contents
        for i, msg in enumerate(request.messages):
            if msg.role == "system":
                print(f"📜 SYSTEM MESSAGE {i}: [SYSTEM PROMPT]")
            else:
                content = str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                print(f"🎤 USER TRANSCRIPT {i}: '{content}'")
        
        print("="*80)
        
        response = await groq_service.generate_response(request)
        
        if request.stream:
            return StreamingResponse(
                response,
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        else:
            return response
            
    except Exception as e:
        print(f"❌ Chat completions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tools_available": TOOLS_AVAILABLE,
        "functions_count": len(AVAILABLE_FUNCTIONS) if TOOLS_AVAILABLE else 0
    }