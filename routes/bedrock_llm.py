from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import boto3
import json
import os
import asyncio
from typing import Dict, Any, List
import uuid
import time

router = APIRouter(prefix="/bedrock", tags=["bedrock"])

class BedrockLLMService:
    def __init__(self):
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

    async def generate_response(self, messages: List[Dict], stream: bool = True):
        try:
            # Load system prompt
            with open('system_prompt.txt', 'r', encoding='utf-8') as f:
                system_prompt = f.read()

            # Format messages for Claude
            formatted_messages = []
            for msg in messages:
                if msg.get('role') == 'user':
                    formatted_messages.append({
                        "role": "user",
                        "content": msg.get('content', '')
                    })
                elif msg.get('role') == 'assistant':
                    formatted_messages.append({
                        "role": "assistant", 
                        "content": msg.get('content', '')
                    })

            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": formatted_messages,
                "temperature": 0.7,
                "top_p": 0.95
            }

            if stream:
                response = self.bedrock_client.invoke_model_with_response_stream(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                return self._stream_response(response)
            else:
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                return json.loads(response['body'].read())

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")

    def _stream_response(self, response):
        """Convert Bedrock streaming response to OpenAI format"""
        for event in response['body']:
            if 'chunk' in event:
                chunk = json.loads(event['chunk']['bytes'])
                if chunk['type'] == 'content_block_delta':
                    yield self._format_chunk(chunk['delta']['text'])
                elif chunk['type'] == 'message_stop':
                    yield "data: [DONE]\n\n"
                    break

    def _format_chunk(self, content: str) -> str:
        """Format chunk in OpenAI streaming format"""
        chunk_data = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": self.model_id,
            "choices": [{
                "index": 0,
                "delta": {"content": content},
                "finish_reason": None
            }]
        }
        return f"data: {json.dumps(chunk_data)}\n\n"

bedrock_service = BedrockLLMService()

@router.post("/chat/completions")
async def chat_completions(request: Dict[Any, Any]):
    try:
        messages = request.get('messages', [])
        stream = request.get('stream', True)
        
        if not stream:
            raise HTTPException(status_code=400, detail="Only streaming is supported")

        async def generate():
            try:
                async for chunk in bedrock_service.generate_response(messages, stream=True):
                    yield chunk
            except Exception as e:
                error_chunk = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion.chunk", 
                    "created": int(time.time()),
                    "model": bedrock_service.model_id,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": f"Error: {str(e)}"},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))