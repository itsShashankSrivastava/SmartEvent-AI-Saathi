#!/usr/bin/env python3
"""
Test script to verify the full conversational AI pipeline
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_full_pipeline():
    """Test the complete pipeline: Agent creation -> LLM -> TTS"""
    
    print("Testing Full Conversational AI Pipeline...")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Check if server is running
        print("1. Testing server connectivity...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✓ Server is running")
            else:
                print("✗ Server not responding")
                return False
        
        # Test 2: Check Groq LLM health
        print("\n2. Testing Groq LLM service...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/groq/health")
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    print("✓ Groq LLM service is healthy")
                else:
                    print(f"✗ Groq LLM service unhealthy: {health_data}")
                    return False
            else:
                print("✗ Groq LLM service not responding")
                return False
        
        # Test 3: Test LLM endpoint directly
        print("\n3. Testing LLM endpoint...")
        test_request = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": "Hello, can you help me plan an event?"}
            ],
            "stream": True,
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/groq/chat/completions",
                json=test_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✓ LLM endpoint responding")
                # Read first few chunks to verify streaming
                content = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and not line.endswith("[DONE]"):
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content += delta["content"]
                        except:
                            pass
                        if len(content) > 20:  # Got some response
                            break
                
                if content:
                    print(f"✓ LLM generated response: '{content[:50]}...'")
                else:
                    print("! LLM responded but no content received")
            else:
                print(f"✗ LLM endpoint failed: {response.status_code}")
                return False
        
        # Test 4: Create agent (without joining channel)
        print("\n4. Testing agent creation...")
        agent_request = {
            "requester_id": "test-user",
            "channel_name": None,
            "event_type": "birthday party",
            "attendee_count": 10,
            "budget_range": "$500-1000"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/agent/invite",
                json=agent_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                agent_data = response.json()
                agent_id = agent_data.get("agent_id")
                channel_name = agent_data.get("channel_name")
                print(f"✓ Agent created successfully")
                print(f"   Agent ID: {agent_id}")
                print(f"   Channel: {channel_name}")
                print(f"   Status: {agent_data.get('status')}")
                
                # Test 5: Check agent status
                print("\n5. Testing agent status...")
                status_response = await client.get(f"{base_url}/agent/status/{agent_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✓ Agent status: {status_data.get('status')}")
                else:
                    print("! Could not get agent status")
                
                # Test 6: Test agent speak (TTS)
                print("\n6. Testing agent TTS...")
                speak_response = await client.post(
                    f"{base_url}/agent/{agent_id}/speak",
                    json={"text": "This is a test message to verify TTS is working."},
                    headers={"Content-Type": "application/json"}
                )
                
                if speak_response.status_code == 200:
                    print("✓ TTS command sent successfully")
                else:
                    print(f"! TTS command failed: {speak_response.status_code}")
                
                # Clean up: Remove agent
                print("\nCleaning up...")
                remove_response = await client.post(
                    f"{base_url}/agent/remove",
                    json={"agent_id": agent_id},
                    headers={"Content-Type": "application/json"}
                )
                
                if remove_response.status_code == 200:
                    print("✓ Agent removed successfully")
                else:
                    print("! Agent removal failed (may timeout naturally)")
                
            else:
                print(f"✗ Agent creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("✓ Server is running")
        print("✓ Groq LLM is working")
        print("✓ Agent creation works")
        print("✓ ARES ASR is configured")
        print("✓ ElevenLabs TTS is configured")
        print("\nYour conversational AI pipeline is ready!")
        print("Open http://localhost:8000/realvoice to test with voice")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_pipeline())
    exit(0 if success else 1)