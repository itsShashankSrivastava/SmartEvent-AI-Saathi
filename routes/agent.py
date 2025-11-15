from fastapi import APIRouter, HTTPException
from typing import Optional
from class_types.agora_types import TTSVendor, ASRVendor, TTSConfig, ASRConfig, AgentResponse, EventPlannerRequest, RemoveAgentRequest
from agora_token_builder import RtcTokenBuilder
import os
import httpx
from datetime import datetime, timedelta
import random
import string
import base64
import time
import json
from pathlib import Path
import asyncio
from typing import Set

router = APIRouter(prefix="/agent", tags=["agent"])

# Track active agents to avoid duplicate saves
active_agents: Set[str] = set()
saved_agents: Set[str] = set()

# Local conversation storage (as backup)
local_conversations = {}

def generate_unique_name(): 
    channel_name_base = 'event-planner'
    timestamp = int(time.time() * 1000)
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
    unique_name = f"{channel_name_base}-{timestamp}-{random_string}"
    return unique_name

def generate_credentials() -> str:
    customer_id = str(os.getenv("AGORA_CUSTOMER_ID"))
    customer_secret = str(os.getenv("AGORA_CUSTOMER_SECRET"))
    credentials = customer_id + ":" + customer_secret
    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")
    return credential

async def generate_token(uid: str, channel: str):
    """Generate token with both RTC and RTM privileges for Conversational AI agents"""
    if not os.getenv("AGORA_APP_ID") or not os.getenv("AGORA_APP_CERTIFICATE"):
        raise HTTPException(status_code=500, detail="Agora credentials are not set")
    
    expiration_time = int(datetime.now().timestamp()) + 3600
    
    try:
        # Generate RTC token with publisher role for the agent
        # According to Agora docs, RTC token can be reused for RTM when enable_rtm is true
        token = RtcTokenBuilder.buildTokenWithUid(
            appId=os.getenv("AGORA_APP_ID"),
            appCertificate=os.getenv("AGORA_APP_CERTIFICATE"),
            channelName=channel,
            uid=int(uid),
            role=1,  # Publisher role for agent
            privilegeExpiredTs=expiration_time
        )
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Agora token: {str(e)}")

def generate_channel_name() -> str:
    timestamp = int(datetime.now().timestamp())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"event-planning-{timestamp}-{random_str}"

def get_tts_config() -> TTSConfig:
    tts_vendor = os.getenv("TTS_VENDOR", "elevenlabs")
    
    if tts_vendor == "elevenlabs":
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_key:
            raise ValueError("ElevenLabs TTS requires ELEVENLABS_API_KEY environment variable")
            
        return TTSConfig(
            vendor=TTSVendor.ELEVENLABS,
            params={
                "key": elevenlabs_key,
                "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_flash_v2_5"),
                "voice_id": os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),
                "sample_rate": 24000
            }
        )
    else:  # Microsoft TTS (fallback)
        microsoft_key = os.getenv("MICROSOFT_TTS_KEY")
        if not microsoft_key:
            raise ValueError("Microsoft TTS requires MICROSOFT_TTS_KEY environment variable")
            
        return TTSConfig(
            vendor=TTSVendor.MICROSOFT,
            params={
                "key": microsoft_key,
                "region": os.getenv("MICROSOFT_TTS_REGION", "eastus"),
                "voice_name": os.getenv("MICROSOFT_TTS_VOICE_NAME", "en-US-AriaNeural"),
                "rate": float(os.getenv("MICROSOFT_TTS_RATE", "1.0")),
                "volume": float(os.getenv("MICROSOFT_TTS_VOLUME", "1.0"))
            }
        )

def get_asr_config() -> dict:
    return {
        "vendor": "ares",
        "language": "en-US"
    }

def load_system_prompt() -> str:
    try:
        with open('system_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful event planning assistant."

def save_conversation_to_file(agent_id: str, conversation_data: dict):
    """Save conversation data to a JSON file"""
    try:
        # Create conversations directory if it doesn't exist
        conversations_dir = Path("conversations")
        conversations_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{agent_id}_{timestamp}.json"
        filepath = conversations_dir / filename
        
        # Save conversation data to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversation saved to: {filepath}")
        return str(filepath)
    except Exception as e:
        print(f"❌ Failed to save conversation: {str(e)}")
        return None

async def auto_save_inactive_agents():
    """Background task to automatically save conversations for inactive agents"""
    while True:
        try:
            print("🔍 Checking for inactive agents to auto-save conversations...")
            
            # Get list of all agents
            async with httpx.AsyncClient() as client:
                credential = generate_credentials()
                
                try:
                    # Get all agents (this endpoint might not exist, so we'll handle gracefully)
                    agents_response = await client.get(
                        f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents",
                        headers={"Authorization": f"Basic {credential}"}
                    )
                    
                    if agents_response.status_code == 200:
                        agents_data = agents_response.json()
                        agents_list = agents_data.get('agents', []) if isinstance(agents_data, dict) else agents_data
                        
                        for agent in agents_list:
                            agent_id = agent.get('agent_id') or agent.get('id')
                            status = agent.get('status', 'unknown')
                            
                            if agent_id and agent_id not in saved_agents:
                                # Check if agent is inactive/idle
                                if status in ['idle', 'inactive', 'disconnected', 'ended']:
                                    print(f"🎯 Found inactive agent {agent_id} with status: {status}")
                                    
                                    # Get detailed agent info and save conversation
                                    try:
                                        status_response = await client.get(
                                            f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}",
                                            headers={"Authorization": f"Basic {credential}"}
                                        )
                                        
                                        if status_response.status_code == 200:
                                            agent_data = status_response.json()
                                            
                                            # Get conversation history
                                            history_response = await client.get(
                                                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}/history",
                                                headers={"Authorization": f"Basic {credential}"}
                                            )
                                            
                                            history_data = history_response.json() if history_response.status_code == 200 else []
                                            
                                            # Format conversation history
                                            formatted_history = []
                                            if isinstance(history_data, list):
                                                for msg in history_data:
                                                    formatted_history.append({
                                                        "timestamp": msg.get("timestamp", "unknown"),
                                                        "role": msg.get("role", "unknown"),
                                                        "content": msg.get("content", ""),
                                                        "type": msg.get("type", "text")
                                                    })
                                            
                                            # Only save if there are actual messages
                                            if len(formatted_history) > 1:
                                                conversation_data = {
                                                    "agent_id": agent_id,
                                                    "status": status,
                                                    "channel_name": agent_data.get("channel_name", "unknown"),
                                                    "created_at": agent_data.get("created_at", "unknown"),
                                                    "auto_saved_at": datetime.now().isoformat(),
                                                    "total_messages": len(formatted_history),
                                                    "conversation_history": formatted_history,
                                                    "last_activity": formatted_history[-1]["timestamp"] if formatted_history else "No activity",
                                                    "agent_info": agent_data,
                                                    "auto_saved": True,
                                                    "save_reason": "background_check_inactive"
                                                }
                                                
                                                saved_file = save_conversation_to_file(agent_id, conversation_data)
                                                if saved_file:
                                                    saved_agents.add(agent_id)
                                                    print(f"✅ Auto-saved conversation for inactive agent {agent_id}")
                                                    
                                    except Exception as agent_error:
                                        print(f"⚠️ Error processing agent {agent_id}: {str(agent_error)}")
                        
                except Exception as list_error:
                    print(f"ℹ️ Could not get agents list (endpoint might not exist): {str(list_error)}")
                    
        except Exception as e:
            print(f"⚠️ Error in auto-save background task: {str(e)}")
        
        # Wait 5 minutes before next check
        await asyncio.sleep(300)

# Start background task (this would typically be started in main.py)
# asyncio.create_task(auto_save_inactive_agents())

@router.get("/webhook/transcript")
async def transcript_webhook_get():
    """GET endpoint for webhook testing"""
    print("🔍 Webhook GET request received")
    return {"status": "webhook active"}

@router.post("/webhook/transcript")
async def transcript_webhook_post(request: dict):
    """POST webhook to capture transcripts"""
    print("\n" + "="*80)
    print("🎤 TRANSCRIPT WEBHOOK TRIGGERED!")
    print(f"📊 Raw data: {request}")
    
    # Extract conversation data
    agent_id = request.get('agent_id')
    transcript = request.get('transcript') or request.get('text') or request.get('message')
    role = request.get('role', 'user')  # Default to user
    timestamp = request.get('timestamp', datetime.now().isoformat())
    
    # Store in local conversation tracker
    if agent_id and transcript:
        if agent_id not in local_conversations:
            local_conversations[agent_id] = []
        
        local_conversations[agent_id].append({
            "timestamp": timestamp,
            "role": role,
            "content": transcript,
            "type": "text",
            "source": "webhook"
        })
        print(f"💾 Stored message locally for agent {agent_id}: {transcript[:50]}...")
    
    if 'transcript' in request:
        print(f"📝 Transcript: {request['transcript']}")
    if 'text' in request:
        print(f"📝 Text: {request['text']}")
    if 'message' in request:
        print(f"📝 Message: {request['message']}")
    
    print("="*80 + "\n")
    return {"status": "received"}

@router.post("/webhook/agent-status")
async def agent_status_webhook(request: dict):
    """Webhook to handle agent status changes (idle, disconnected, etc.)"""
    print("\n" + "="*80)
    print("🤖 AGENT STATUS WEBHOOK TRIGGERED!")
    print(f"📊 Raw data: {request}")
    
    try:
        agent_id = request.get('agent_id')
        status = request.get('status')
        event_type = request.get('event_type', request.get('type'))
        
        print(f"🆔 Agent ID: {agent_id}")
        print(f"📊 Status: {status}")
        print(f"🎯 Event Type: {event_type}")
        
        # Auto-save conversation when agent becomes idle or disconnected
        if agent_id and event_type in ['agent_idle', 'agent_disconnected', 'session_ended', 'agent_timeout']:
            print(f"💾 Auto-saving conversation for agent {agent_id} due to {event_type}")
            
            try:
                async with httpx.AsyncClient() as client:
                    credential = generate_credentials()
                    
                    # Get agent status and history
                    status_response = await client.get(
                        f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}",
                        headers={"Authorization": f"Basic {credential}"}
                    )
                    
                    if status_response.status_code == 200:
                        agent_data = status_response.json()
                        
                        # Get conversation history
                        history_response = await client.get(
                            f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}/history",
                            headers={"Authorization": f"Basic {credential}"}
                        )
                        
                        history_data = history_response.json() if history_response.status_code == 200 else []
                        
                        # Format conversation history
                        formatted_history = []
                        if isinstance(history_data, list):
                            for msg in history_data:
                                formatted_history.append({
                                    "timestamp": msg.get("timestamp", "unknown"),
                                    "role": msg.get("role", "unknown"),
                                    "content": msg.get("content", ""),
                                    "type": msg.get("type", "text")
                                })
                        
                        # Only save if there are actual messages (more than just greeting)
                        if len(formatted_history) > 1:
                            # Prepare conversation data
                            conversation_data = {
                                "agent_id": agent_id,
                                "status": agent_data.get("status", "unknown"),
                                "channel_name": agent_data.get("channel_name", "unknown"),
                                "created_at": agent_data.get("created_at", "unknown"),
                                "auto_saved_at": datetime.now().isoformat(),
                                "total_messages": len(formatted_history),
                                "conversation_history": formatted_history,
                                "last_activity": formatted_history[-1]["timestamp"] if formatted_history else "No activity",
                                "agent_info": agent_data,
                                "auto_saved": True,
                                "save_reason": event_type,
                                "webhook_data": request
                            }
                            
                            # Save to file
                            saved_file = save_conversation_to_file(agent_id, conversation_data)
                            if saved_file:
                                print(f"✅ Conversation automatically saved to: {saved_file}")
                            else:
                                print(f"⚠️ Failed to save conversation for agent {agent_id}")
                        else:
                            print(f"ℹ️ No meaningful conversation to save for agent {agent_id} (only {len(formatted_history)} messages)")
                            
            except Exception as save_error:
                print(f"⚠️ Error auto-saving conversation: {str(save_error)}")
        
    except Exception as e:
        print(f"❌ Error processing agent status webhook: {str(e)}")
    
    print("="*80 + "\n")
    return {"status": "received", "processed": True}

@router.get("/test-transcript")
async def test_transcript():
    """Test endpoint to simulate transcript"""
    print("\n" + "="*50)
    print("🧪 TEST TRANSCRIPT:")
    print("📝 This is a test transcript to verify logging works")
    print("="*50 + "\n")
    return {"message": "Test transcript logged to console"}

@router.post("/invite", response_model=AgentResponse)
async def invite_agent(request: EventPlannerRequest):
    try:
        name = generate_unique_name()
        channel_name = request.channel_name or generate_channel_name()
        print(f"DEBUG: Request channel_name: {request.channel_name}")
        print(f"DEBUG: Generated channel_name: {channel_name}")
        print(f"DEBUG: Channel_name type: {type(channel_name)}")
        token = await generate_token(uid=os.getenv("AGENT_UID"), channel=channel_name)
        
        tts_config = get_tts_config()
        asr_config = get_asr_config()
        system_prompt = load_system_prompt()

        request_body = {
            "name": name,
            # ✅ AFTER (routes/agent.py)
            "properties": {
                "channel": channel_name,
                "token": token,
                "agent_rtc_uid": str(os.getenv("AGENT_UID")), # <-- CHANGED TO INT
                "remote_rtc_uids": ["12345"],                   # <-- CHANGED TO INT ARRAY
                "enable_string_uid": False,                 # <-- ADDED THIS
             "idle_timeout": 300,
                "voice_activity_detection": {
                    "enabled": True
                },
                "asr": asr_config,
                "llm": {
                    "url": os.getenv("LLM_URL"),
                    "api_key": os.getenv("GROQ_API_KEY"),
                    "vendor": "custom",
                    "style": "openai",
                    "system_messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ],
                    "greeting_message": "Hello! I'm EventMaster Pro, your professional event planning consultant. How may I assist you with your event planning needs today?",
                    "failure_message": "I didn't catch that. Could you please repeat?",
                    "max_history": 10,
                    "timeout": 30,
                    "params": {
                        "model": "llama-3.1-8b-instant",
                        "max_tokens": 150,
                        "temperature": 0.7,
                        "stream": True,
                    }
                },
                "greeting": {
                    "enabled": True,
                    "message": "Hello! I'm EventMaster Pro, your professional event planning consultant. How may I assist you with your event planning needs today?"
                },
                "tts": tts_config.dict(),
                "turn_detection": {
                    "type": "server_vad",
                    "silence_duration_ms": 1000,
                    "threshold": 0.5
                },
                "advanced_features": {
                    "enable_rtm": True
                },
                "parameters": {
                    "data_channel": "rtm"
                },

            }
        }

        print(f"DEBUG: 🔧 ARES ASR CONFIGURATION SUMMARY:")
        print(f"DEBUG: Vendor: {asr_config.get('vendor')}")
        print(f"DEBUG: Language: {asr_config.get('language')}")
        print(f"DEBUG: Using Agora's built-in ARES ASR for real-time speech recognition")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            credential = generate_credentials()
            agora_url = f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/join"
            
            print(f"DEBUG: Sending request to: {agora_url}")
            print(f"DEBUG: Agent UID: {request_body['properties']['agent_rtc_uid']} (type: {type(request_body['properties']['agent_rtc_uid'])})")
            print(f"DEBUG: Remote UIDs: {request_body['properties']['remote_rtc_uids']}")
            print(f"DEBUG: Greeting Message: {request_body['properties']['llm']['greeting_message']}")
            print(f"DEBUG: TTS Vendor: {request_body['properties']['tts']['vendor']}")
            asr_config = request_body['properties']['asr']
            print(f"DEBUG: ASR Vendor: {asr_config['vendor']}")
            print(f"DEBUG: ASR Language: {asr_config['language']}")
            print(f"DEBUG: ASR Config: {asr_config}")
            print(f"DEBUG: ARES ASR - No additional configuration needed")
            print(f"DEBUG: ARES provides built-in real-time speech-to-text with low latency")
            print(f"DEBUG: Idle Timeout: {request_body['properties']['idle_timeout']}")
            print(f"DEBUG: Voice Activity Detection: {request_body['properties']['voice_activity_detection']}")
            print(f"DEBUG: Turn Detection: {request_body['properties']['turn_detection']}")
            print(f"DEBUG: LLM URL: {request_body['properties']['llm']['url']}")
            print(f"DEBUG: LLM API Key: {request_body['properties']['llm']['api_key'][:20]}...")
            print(f"DEBUG: LLM Model: {request_body['properties']['llm']['params']['model']}")
            print(f"DEBUG: LLM Max Tokens: {request_body['properties']['llm']['params']['max_tokens']}")
            print(f"\n🔊 TRANSCRIPT DEBUGGING: Check LLM endpoint logs")
            print(f"🎤 User speech will be processed by ARES ASR and sent to LLM\n")
            
            response = await client.post(
                agora_url,
                json=request_body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {credential}"
                }
            )
            
            print(f"DEBUG: Agora response status: {response.status_code}")
            print(f"DEBUG: Agora response: {response.text}")
            
            if response.status_code == 200:
                print(f"DEBUG: ✅ Agent created successfully with ARES ASR configuration")
                print(f"DEBUG: 🎤 Audio will be processed by ARES ASR with:")
                print(f"DEBUG:    - Vendor: {asr_config.get('vendor')} (ares)")
                print(f"DEBUG:    - Language: {asr_config.get('language')} (en-US)")
                print(f"DEBUG:    - Built-in real-time speech-to-text with low latency")
                print(f"DEBUG: 🔊 ARES ASR should provide reliable speech recognition")
            else:
                print(f"DEBUG: ❌ Agent creation failed with status {response.status_code}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agora API error: {response.text}"
                )
            
            # Get the Agora response and add our channel name
            agora_response = response.json()
            agora_response["channel_name"] = channel_name
            agora_response["token"] = token
            
            # Track this agent as active
            agent_id = agora_response.get("agent_id")
            if agent_id:
                active_agents.add(agent_id)
                print(f"📝 Added agent {agent_id} to active tracking")
            
            print(f"DEBUG: Returning response with channel_name: {channel_name}")
            print(f"DEBUG: Full response: {agora_response}")
            print(f"DEBUG: 🎯 ARES ASR CONFIGURATION DETAILS:")
            print(f"DEBUG:    ✅ Using Agora's built-in ARES ASR")
            print(f"DEBUG:    ✅ No external API keys required")
            print(f"DEBUG:    ✅ Optimized for conversational AI with low latency")
            print(f"DEBUG:    ✅ Language set to en-US for English recognition")
            print(f"DEBUG: 📊 Expected flow: Audio → ARES ASR → Transcript → LLM → TTS → Response")
            print(f"DEBUG: 💾 Conversation will be auto-saved when session ends")
            
            # Trigger greeting message after a short delay
            # try:
            #     import asyncio
            #     await asyncio.sleep(2)  # Wait for agent to be fully ready
                
            #     greeting_response = await client.post(
            #         f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agora_response['agent_id']}/speak",
            #         json={"text": "Hello! I'm EventBot, your voice assistant for event planning. How can I help you today?"},
            #         headers={
            #             "Content-Type": "application/json",
            #             "Authorization": f"Basic {credential}"
            #         }
            #     )
                
            #     if greeting_response.status_code == 200:
            #         print(f"DEBUG: ✅ Greeting message triggered successfully")
            #     else:
            #         print(f"DEBUG: ⚠️ Greeting trigger failed: {greeting_response.status_code}")
                    
            # except Exception as greeting_error:
            #     print(f"DEBUG: ⚠️ Greeting trigger error: {greeting_error}")
            
            return agora_response
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = f"Exception: {str(e)}, Traceback: {traceback.format_exc()}"
        print(f"DEBUG: Agent creation error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to start event planning session: {error_details}")

@router.post("/remove")
async def remove_agent(request: RemoveAgentRequest):
    try:
        async with httpx.AsyncClient() as client:
            credential = generate_credentials()
            
            # First, save the conversation before ending the session
            try:
                print(f"💾 Automatically saving conversation for agent {request.agent_id} before ending session...")
                
                # Get agent status and history
                status_response = await client.get(
                    f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{request.agent_id}",
                    headers={"Authorization": f"Basic {credential}"}
                )
                
                if status_response.status_code == 200:
                    agent_data = status_response.json()
                    
                    # Get conversation history
                    history_response = await client.get(
                        f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{request.agent_id}/history",
                        headers={"Authorization": f"Basic {credential}"}
                    )
                    
                    print(f"🔍 History API response status: {history_response.status_code}")
                    print(f"🔍 History API response: {history_response.text}")
                    
                    history_data = history_response.json() if history_response.status_code == 200 else []
                    print(f"🔍 History data type: {type(history_data)}")
                    print(f"🔍 History data: {history_data}")
                    
                    # Format conversation history
                    formatted_history = []
                    if isinstance(history_data, list):
                        for msg in history_data:
                            formatted_history.append({
                                "timestamp": msg.get("timestamp", "unknown"),
                                "role": msg.get("role", "unknown"),
                                "content": msg.get("content", ""),
                                "type": msg.get("type", "text")
                            })
                    elif isinstance(history_data, dict):
                        # Agora API returns data in 'contents' field
                        messages = (history_data.get('contents', []) or 
                                  history_data.get('messages', []) or 
                                  history_data.get('history', []) or 
                                  history_data.get('conversation', []))
                        
                        for msg in messages:
                            formatted_history.append({
                                "timestamp": msg.get("timestamp", "unknown"),
                                "role": msg.get("role", "unknown"),
                                "content": msg.get("content", ""),
                                "type": msg.get("type", "text"),
                                "metadata": msg.get("metadata", {}),
                                "turn_id": msg.get("turn_id", "unknown")
                            })
                    
                    print(f"🔍 Formatted history length: {len(formatted_history)}")
                    print(f"🔍 Formatted history: {formatted_history}")
                    
                    # If no history from API, try local conversation storage
                    if len(formatted_history) == 0 and request.agent_id in local_conversations:
                        formatted_history = local_conversations[request.agent_id]
                        print(f"🔄 Using local conversation storage: {len(formatted_history)} messages")
                    
                    # Save conversation even if empty (for debugging purposes)
                    should_save = True  # Always save for now to debug
                    if should_save:
                        # Prepare conversation data
                        conversation_data = {
                            "agent_id": request.agent_id,
                            "status": agent_data.get("status", "unknown"),
                            "channel_name": agent_data.get("channel_name", "unknown"),
                            "created_at": agent_data.get("created_at", "unknown"),
                            "session_ended_at": datetime.now().isoformat(),
                            "total_messages": len(formatted_history),
                            "conversation_history": formatted_history,
                            "last_activity": formatted_history[-1]["timestamp"] if formatted_history else "No activity",
                            "agent_info": agent_data,
                            "auto_saved": True,
                            "save_reason": "session_ended",
                            "debug_info": {
                                "history_api_status": history_response.status_code,
                                "history_api_response": history_response.text,
                                "raw_history_data": history_data
                            }
                        }
                        
                        # Save to file
                        saved_file = save_conversation_to_file(request.agent_id, conversation_data)
                        if saved_file:
                            print(f"✅ Conversation automatically saved to: {saved_file}")
                        else:
                            print(f"⚠️ Failed to save conversation for agent {request.agent_id}")
                    else:
                        print(f"ℹ️ No meaningful conversation to save for agent {request.agent_id} (only {len(formatted_history)} messages)")
                        
            except Exception as save_error:
                print(f"⚠️ Error saving conversation before ending session: {str(save_error)}")
                # Continue with session termination even if save fails
            
            # Now end the session
            response = await client.post(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{request.agent_id}/leave",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {credential}"
                }
            )
            response.raise_for_status()
            
            result = response.json()
            result["conversation_auto_saved"] = True
            
            # Generate event summary automatically
            try:
                if saved_file and len(formatted_history) > 1:
                    print(f"📊 Generating event summary for agent {request.agent_id}...")
                    
                    # Import and generate summary
                    import sys
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    
                    from event_summary import generate_event_summary
                    summary_result = generate_event_summary(conversation_data)
                    
                    if summary_result["success"]:
                        result["summary_generated"] = True
                        result["summary_url"] = summary_result["url"]
                        result["summary_filename"] = summary_result["filename"]
                        print(f"✅ Event summary generated: {summary_result['filename']}")
                    else:
                        print(f"⚠️ Summary generation failed: {summary_result.get('error', 'Unknown error')}")
                        result["summary_generated"] = False
                        
            except Exception as summary_error:
                print(f"⚠️ Error generating summary: {str(summary_error)}")
                result["summary_generated"] = False
            
            # Remove from active tracking and add to saved tracking
            active_agents.discard(request.agent_id)
            saved_agents.add(request.agent_id)
            
            print(f"🏁 Session ended for agent {request.agent_id}")
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end event planning session: {str(e)}")

@router.get("/status/{agent_id}")
async def get_agent_status(agent_id: str):
    try:
        async with httpx.AsyncClient() as client:
            credential = generate_credentials()
            response = await client.get(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}",
                headers={
                    "Authorization": f"Basic {credential}"
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

@router.get("/history/{agent_id}")
async def get_agent_history(agent_id: str):
    try:
        async with httpx.AsyncClient() as client:
            credential = generate_credentials()
            response = await client.get(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}/history",
                headers={
                    "Authorization": f"Basic {credential}"
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@router.post("/{agent_id}/speak")
async def agent_speak(agent_id: str, request: dict):
    """Make the agent speak a custom message using TTS"""
    try:
        async with httpx.AsyncClient() as client:
            credential = generate_credentials()
            response = await client.post(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}/speak",
                json=request,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {credential}"
                }
            )
            response.raise_for_status()
            return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to make agent speak: {str(e)}")

@router.get("/monitor/{agent_id}")
async def monitor_agent(agent_id: str):
    """Monitor agent with real-time status and conversation history"""
    try:
        async with httpx.AsyncClient() as client:
            credential = generate_credentials()
            
            # Get agent status
            status_response = await client.get(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}",
                headers={"Authorization": f"Basic {credential}"}
            )
            
            if status_response.status_code == 404:
                return {"error": "Agent not found", "agent_id": agent_id}
            
            agent_data = status_response.json()
            
            # Get conversation history
            history_response = await client.get(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}/history",
                headers={"Authorization": f"Basic {credential}"}
            )
            
            history_data = history_response.json() if history_response.status_code == 200 else []
            
            # Format for easy reading
            formatted_history = []
            if isinstance(history_data, list):
                for msg in history_data:
                    formatted_history.append({
                        "timestamp": msg.get("timestamp", "unknown"),
                        "role": msg.get("role", "unknown"),
                        "content": msg.get("content", ""),
                        "type": msg.get("type", "text")
                    })
            
            # Prepare complete conversation data
            conversation_data = {
                "agent_id": agent_id,
                "status": agent_data.get("status", "unknown"),
                "channel_name": agent_data.get("channel_name", "unknown"),
                "created_at": agent_data.get("created_at", "unknown"),
                "monitored_at": datetime.now().isoformat(),
                "total_messages": len(formatted_history),
                "conversation_history": formatted_history,
                "last_activity": formatted_history[-1]["timestamp"] if formatted_history else "No activity",
                "agent_info": agent_data
            }
            
            # Save conversation to file
            saved_file = save_conversation_to_file(agent_id, conversation_data)
            if saved_file:
                conversation_data["saved_to_file"] = saved_file
            
            return conversation_data
            
    except Exception as e:
        return {"error": f"Monitor failed: {str(e)}", "agent_id": agent_id}

@router.post("/save-conversation/{agent_id}")
async def save_conversation(agent_id: str):
    """Manually save conversation to JSON file"""
    try:
        async with httpx.AsyncClient() as client:
            credential = generate_credentials()
            
            # Get agent status
            status_response = await client.get(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}",
                headers={"Authorization": f"Basic {credential}"}
            )
            
            if status_response.status_code == 404:
                return {"error": "Agent not found", "agent_id": agent_id}
            
            agent_data = status_response.json()
            
            # Get conversation history
            history_response = await client.get(
                f"{os.getenv('AGORA_CONVO_AI_BASE_URL')}/{os.getenv('AGORA_APP_ID')}/agents/{agent_id}/history",
                headers={"Authorization": f"Basic {credential}"}
            )
            
            history_data = history_response.json() if history_response.status_code == 200 else []
            
            # Format conversation history
            formatted_history = []
            if isinstance(history_data, list):
                for msg in history_data:
                    formatted_history.append({
                        "timestamp": msg.get("timestamp", "unknown"),
                        "role": msg.get("role", "unknown"),
                        "content": msg.get("content", ""),
                        "type": msg.get("type", "text")
                    })
            
            # Prepare conversation data
            conversation_data = {
                "agent_id": agent_id,
                "status": agent_data.get("status", "unknown"),
                "channel_name": agent_data.get("channel_name", "unknown"),
                "created_at": agent_data.get("created_at", "unknown"),
                "saved_at": datetime.now().isoformat(),
                "total_messages": len(formatted_history),
                "conversation_history": formatted_history,
                "last_activity": formatted_history[-1]["timestamp"] if formatted_history else "No activity",
                "agent_info": agent_data
            }
            
            # Save to file
            saved_file = save_conversation_to_file(agent_id, conversation_data)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "saved_to": saved_file,
                "total_messages": len(formatted_history),
                "message": "Conversation saved successfully"
            }
            
    except Exception as e:
        return {"error": f"Failed to save conversation: {str(e)}", "agent_id": agent_id}

@router.get("/conversations")
async def list_saved_conversations():
    """List all saved conversation files"""
    try:
        conversations_dir = Path("conversations")
        if not conversations_dir.exists():
            return {"conversations": [], "message": "No conversations directory found"}
        
        conversation_files = []
        for file_path in conversations_dir.glob("conversation_*.json"):
            try:
                # Get file info
                stat = file_path.stat()
                file_info = {
                    "filename": file_path.name,
                    "filepath": str(file_path),
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
                # Try to read basic info from the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        file_info.update({
                            "agent_id": data.get("agent_id", "unknown"),
                            "total_messages": data.get("total_messages", 0),
                            "status": data.get("status", "unknown"),
                            "channel_name": data.get("channel_name", "unknown")
                        })
                except:
                    file_info["error"] = "Could not read file content"
                
                conversation_files.append(file_info)
            except Exception as e:
                conversation_files.append({
                    "filename": file_path.name,
                    "error": f"Could not read file info: {str(e)}"
                })
        
        # Sort by creation time (newest first)
        conversation_files.sort(key=lambda x: x.get("created", ""), reverse=True)
        
        return {
            "conversations": conversation_files,
            "total_files": len(conversation_files),
            "directory": str(conversations_dir)
        }
        
    except Exception as e:
        return {"error": f"Failed to list conversations: {str(e)}"}

@router.get("/conversations/{filename}")
async def get_saved_conversation(filename: str):
    """Retrieve a specific saved conversation file"""
    try:
        conversations_dir = Path("conversations")
        file_path = conversations_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Conversation file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
        
        return conversation_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read conversation: {str(e)}")

@router.post("/start-auto-save-monitor")
async def start_auto_save_monitor():
    """Start the background task to monitor and auto-save conversations"""
    try:
        # Start the background task
        asyncio.create_task(auto_save_inactive_agents())
        return {
            "status": "started",
            "message": "Auto-save monitoring started",
            "check_interval": "5 minutes",
            "active_agents": len(active_agents),
            "saved_agents": len(saved_agents)
        }
    except Exception as e:
        return {"error": f"Failed to start auto-save monitor: {str(e)}"}

@router.get("/auto-save-status")
async def get_auto_save_status():
    """Get status of auto-save functionality"""
    return {
        "active_agents": list(active_agents),
        "saved_agents": list(saved_agents),
        "total_active": len(active_agents),
        "total_saved": len(saved_agents),
        "local_conversations": {k: len(v) for k, v in local_conversations.items()},
        "conversations_directory": "conversations/",
        "auto_save_triggers": [
            "Manual session end via /agent/remove",
            "Agent status webhook (idle/disconnected)",
            "Background monitoring task (every 5 minutes)"
        ]
    }

@router.post("/test-add-conversation/{agent_id}")
async def test_add_conversation(agent_id: str, message: dict):
    """Test endpoint to manually add conversation messages"""
    try:
        if agent_id not in local_conversations:
            local_conversations[agent_id] = []
        
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": message.get("role", "user"),
            "content": message.get("content", ""),
            "type": "text",
            "source": "manual_test"
        }
        
        local_conversations[agent_id].append(conversation_entry)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "message_added": conversation_entry,
            "total_messages": len(local_conversations[agent_id])
        }
    except Exception as e:
        return {"error": f"Failed to add test conversation: {str(e)}"}

@router.get("/debug/config")
async def debug_config():
    """Debug endpoint to check agent configuration"""
    try:
        tts_config = get_tts_config()
        asr_config = get_asr_config()
        
        return {
            "status": "ok",
            "agora_config": {
                "app_id": os.getenv("AGORA_APP_ID")[:8] + "..." if os.getenv("AGORA_APP_ID") else "NOT_SET",
                "app_certificate": "SET" if os.getenv("AGORA_APP_CERTIFICATE") else "NOT_SET",
                "customer_id": "SET" if os.getenv("AGORA_CUSTOMER_ID") else "NOT_SET",
                "customer_secret": "SET" if os.getenv("AGORA_CUSTOMER_SECRET") else "NOT_SET",
                "agent_uid": os.getenv("AGENT_UID"),
                "base_url": os.getenv("AGORA_CONVO_AI_BASE_URL")
            },
            "asr_config": asr_config,
            "tts_config": {
                "vendor": tts_config.vendor.value,
                "api_key_set": "SET" if tts_config.params.get("key") else "NOT_SET"
            },
            "llm_config": {
                "url": os.getenv("LLM_URL"),
                "api_key_set": "SET" if os.getenv("GROQ_API_KEY") else "NOT_SET",
                "model": "llama-3.1-8b-instant"
            },
            "system_prompt_loaded": "YES" if load_system_prompt() != "You are a helpful event planning assistant." else "NO (using default)",
            "auto_save_config": {
                "active_agents": len(active_agents),
                "saved_agents": len(saved_agents),
                "conversations_directory": "conversations/"
            }
        }
    except Exception as e:
        return {"error": f"Config debug failed: {str(e)}"}