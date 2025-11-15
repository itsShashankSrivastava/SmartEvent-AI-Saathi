#!/usr/bin/env python3
"""
Demo script showing the enhanced voice bot with function calling
Run this after starting your main.py server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def demo_voice_bot_with_function_calling():
    """Demonstrate the voice bot's new function calling capabilities"""
    
    print("🎤 EventBot Voice Assistant Demo with Function Calling")
    print("=" * 60)
    
    # Simulate voice conversations that would trigger search
    conversations = [
        {
            "title": "Wedding Planning in Delhi",
            "user_input": "Hi, I want to plan my wedding in Delhi for 250 people. My budget is around 4 lakhs. Can you help me find venues?",
            "expected": "Should recommend specific Delhi wedding venues with pricing"
        },
        {
            "title": "Birthday Party in Mumbai", 
            "user_input": "I need to organize a birthday party in Mumbai for 80 people. What venues would you recommend?",
            "expected": "Should suggest Mumbai birthday venues with capacity 80+"
        },
        {
            "title": "Corporate Event Catering",
            "user_input": "I'm organizing a corporate event in Bangalore for 150 people. I need food catering recommendations.",
            "expected": "Should recommend Bangalore food vendors for corporate events"
        },
        {
            "title": "Budget Planning",
            "user_input": "What would be the budget for a wedding with 200 guests in Chennai?",
            "expected": "Should provide detailed budget breakdown"
        }
    ]
    
    for i, conversation in enumerate(conversations, 1):
        print(f"\n{i}️⃣ {conversation['title']}")
        print(f"👤 User: {conversation['user_input']}")
        print(f"🎯 Expected: {conversation['expected']}")
        print("-" * 50)
        
        try:
            # Simulate the voice bot request (same as what Agora would send)
            llm_request = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "user", 
                        "content": conversation['user_input']
                    }
                ],
                "stream": False,  # Using non-streaming for demo
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            print("🤖 EventBot: Processing your request...")
            
            response = requests.post(f"{BASE_URL}/groq/chat/completions", json=llm_request)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    bot_response = data['choices'][0]['message']['content']
                    
                    # Display the response
                    print(f"🤖 EventBot: {bot_response}")
                    
                    # Check if it contains search data
                    search_indicators = [
                        'Imperial Banquet', 'Royal Garden', 'Sea View', 'Garden City',
                        'Tamil Heritage', 'Cyberabad', 'Tech Hub', 'Grand Palace',
                        'Spice Route', 'Mumbai Flower', 'Bangalore Blooms',
                        '₹', 'Rating:', 'Contact:', 'Capacity:', 'per person'
                    ]
                    
                    found_indicators = [ind for ind in search_indicators if ind in bot_response]
                    
                    if found_indicators:
                        print(f"✅ Search Integration Active - Found: {len(found_indicators)} specific details")
                    else:
                        print(f"⚠️ Generic response - Search may not have triggered")
                        
                else:
                    print("❌ Unexpected response format")
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Please start the server with: python main.py")
            return
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "=" * 60)
    
    print("\n🎉 Demo completed!")
    print("\n💡 How it works:")
    print("1. User speaks to the voice bot (via Agora)")
    print("2. Speech is converted to text (ARES ASR)")
    print("3. Text is sent to your LLM endpoint")
    print("4. LLM detects if search is needed and enhances the query")
    print("5. Search results are added to the context")
    print("6. LLM generates response with specific venue/vendor recommendations")
    print("7. Response is converted to speech (ElevenLabs TTS)")
    print("8. User hears specific, realistic recommendations!")

def test_search_detection():
    """Test what triggers search enhancement"""
    print("\n🔍 Testing Search Detection...")
    
    test_phrases = [
        "Hello, how are you?",  # Should NOT trigger search
        "I need a venue in Delhi",  # Should trigger search
        "What's the weather like?",  # Should NOT trigger search
        "Can you recommend food catering?",  # Should trigger search
        "Budget for wedding 200 people",  # Should trigger search
    ]
    
    for phrase in test_phrases:
        search_keywords = [
            'venue', 'hall', 'banquet', 'place', 'location', 'where',
            'vendor', 'caterer', 'food', 'photographer', 'music', 'dj',
            'flower', 'decoration', 'budget', 'cost', 'price', 'recommend'
        ]
        
        phrase_lower = phrase.lower()
        would_trigger = any(keyword in phrase_lower for keyword in search_keywords)
        
        status = "🔍 SEARCH" if would_trigger else "💬 CHAT"
        print(f"{status}: '{phrase}'")

if __name__ == "__main__":
    test_search_detection()
    demo_voice_bot_with_function_calling()