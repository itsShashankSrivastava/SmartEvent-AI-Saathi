#!/usr/bin/env python3
"""
Test script to verify TTS configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tts_config():
    print("🔊 Testing TTS Configuration...")
    print("=" * 50)
    
    # Check ElevenLabs configuration
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID")
    elevenlabs_model = os.getenv("ELEVENLABS_MODEL_ID")
    tts_vendor = os.getenv("TTS_VENDOR")
    
    print(f"TTS Vendor: {tts_vendor}")
    print(f"ElevenLabs API Key: {'✅ SET' if elevenlabs_key else '❌ NOT SET'}")
    if elevenlabs_key:
        print(f"  Key preview: {elevenlabs_key[:10]}...")
    
    print(f"ElevenLabs Voice ID: {'✅ SET' if elevenlabs_voice else '❌ NOT SET'}")
    if elevenlabs_voice:
        print(f"  Voice ID: {elevenlabs_voice}")
    
    print(f"ElevenLabs Model ID: {'✅ SET' if elevenlabs_model else '❌ NOT SET'}")
    if elevenlabs_model:
        print(f"  Model ID: {elevenlabs_model}")
    
    print("\n🔧 Testing TTS Config Function...")
    try:
        from routes.agent import get_tts_config
        tts_config = get_tts_config()
        print(f"✅ TTS Config loaded successfully")
        print(f"  Vendor: {tts_config.vendor}")
        print(f"  Voice ID: {tts_config.params.get('voice_id')}")
        print(f"  Model ID: {tts_config.params.get('model_id')}")
        print(f"  Sample Rate: {tts_config.params.get('sample_rate')}")
        
        # Test the configuration format
        tts_dict = {
            "vendor": tts_config.vendor.value,
            "key": tts_config.params.get("key"),
            "model_id": tts_config.params.get("model_id", "eleven_flash_v2_5"),
            "voice_id": tts_config.params.get("voice_id", "EXAVITQu4vr4xnSDxMaL"),
            "sample_rate": tts_config.params.get("sample_rate", 24000)
        }
        print(f"✅ TTS Dict format: {tts_dict}")
        
    except Exception as e:
        print(f"❌ TTS Config error: {e}")
    
    print("\n🎤 Testing ASR Config...")
    try:
        from routes.agent import get_asr_config
        asr_config = get_asr_config()
        print(f"✅ ASR Config: {asr_config}")
    except Exception as e:
        print(f"❌ ASR Config error: {e}")
    
    print("\n📝 Testing System Prompt...")
    try:
        from system_prompt import get_system_prompt
        prompt = get_system_prompt()
        print(f"✅ System prompt loaded: {len(prompt)} characters")
        print(f"  Preview: {prompt[:100]}...")
    except Exception as e:
        print(f"❌ System prompt error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    
    if not elevenlabs_key:
        print("❌ Set ELEVENLABS_API_KEY in .env file")
    if not elevenlabs_voice:
        print("❌ Set ELEVENLABS_VOICE_ID in .env file")
    if tts_vendor != "elevenlabs":
        print("❌ Set TTS_VENDOR=elevenlabs in .env file")
    
    if elevenlabs_key and elevenlabs_voice and tts_vendor == "elevenlabs":
        print("✅ TTS configuration looks good!")
        print("✅ Try restarting the server and creating a new agent")

if __name__ == "__main__":
    test_tts_config()