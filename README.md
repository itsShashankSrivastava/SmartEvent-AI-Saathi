# Conversational Event Planner

An AI-powered event planning assistant that helps organize community events, family gatherings, and group outings through natural voice conversations. This system provides end-to-end event planning capabilities with intelligent venue and vendor recommendations, budget estimation, and automated conversation summaries.

## Demo Video Link
https://drive.google.com/file/d/1AdGSb0QNAvEfsbzgKXYSH6m_-slbbEN1/view?usp=sharing

## Application Screenshots
<img width="1919" height="946" alt="Screenshot 2025-11-15 054916" src="https://github.com/user-attachments/assets/3735a6a7-bfd9-4ea0-aa01-209e10ffc987" />
<img width="1840" height="834" alt="Screenshot 2025-11-15 061221" src="https://github.com/user-attachments/assets/e1a55d64-8c6c-4b31-aabc-cf28b44e6d22" />
<img width="1848" height="823" alt="Screenshot 2025-11-15 075647" src="https://github.com/user-attachments/assets/44be5b2f-9c1c-4bda-87e9-4dec9b7ff547" />
<img width="598" height="829" alt="image (1)" src="https://github.com/user-attachments/assets/a0af2230-225b-4b5c-a1a3-6bcc57ed524c" />
<img width="1394" height="600" alt="Screenshot 2025-11-16 001929" src="https://github.com/user-attachments/assets/db626447-929e-4e1c-a5df-2c3945aa0cd1" />


## 🎯 Project Overview

This project creates a complete voice-first event planning experience where users can:
1. **Talk naturally** to an AI assistant about their event needs
2. **Get intelligent recommendations** for venues, vendors, and budgets
3. **Receive real-time responses** with venue details, pricing, and contact information
4. **Generate professional summaries** of their planning session (HTML & PDF formats)
5. **Access comprehensive event data** for major Indian cities
6. **Auto-save conversations** with multiple backup mechanisms

## ✨ Key Features

- **🎤 Voice-First Interaction**: Natural conversation using Agora's Conversational AI Engine with ARES ASR
- **🤖 Intelligent Event Planning**: AI assistant with enhanced function calling capabilities for real venue/vendor search
- **🏢 Smart Venue Recommendations**: Real venue data across 11+ Indian cities with capacity, pricing, and ratings
- **👥 Vendor Marketplace**: Comprehensive vendor database (caterers, photographers, decorators, etc.)
- **💰 Dynamic Budget Estimation**: City-specific pricing with detailed cost breakdowns
- **📊 Automated Summaries**: Professional HTML & PDF reports with budget visualizations
- **🔄 Real-time Communication**: Low-latency voice interaction powered by Agora SDRTN®
- **💾 Advanced Conversation Tracking**: Multi-layer auto-save with webhooks, background monitoring, and manual triggers
- **🔧 Enhanced Function Calling**: Intelligent query parsing with automatic venue/vendor search based on natural language

## 🛠 Technology Stack

- **Backend**: FastAPI (Python) with async support and enhanced error handling
- **AI/LLM**: Groq (Llama 3.1) with OpenAI-compatible API and streaming support
- **Function Calling**: Enhanced event planning tools with intelligent query parsing
- **Text-to-Speech**: ElevenLabs with Indian English voice optimization and TTS-friendly text cleaning
- **Speech Recognition**: ARES ASR (Agora's built-in, optimized for conversational AI)
- **Real-time Communication**: Agora Conversational AI Engine with webhook support
- **Data Storage**: JSON-based event database with 1000+ venues and vendors
- **Document Generation**: ReportLab + Matplotlib for professional HTML & PDF summaries
- **Authentication**: Agora RTC Token Authentication with enhanced security
- **Conversation Management**: Multi-layer auto-save system with background monitoring

## 🚀 Quick Start Guide

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Update the `.env` file with your API credentials:

```bash
# Agora Configuration (Required)
AGORA_APP_ID=your_agora_app_id
AGORA_APP_CERTIFICATE=your_agora_app_certificate
AGORA_CUSTOMER_ID=your_agora_customer_id
AGORA_CUSTOMER_SECRET=your_agora_customer_secret
AGORA_CONVO_AI_BASE_URL=https://api.agora.io/api/conversational-ai-agent/v2/projects
AGENT_UID=10001

# Groq LLM Configuration (Required)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
# For local development:
LLM_URL=http://localhost:8000/groq/chat/completions
# For production with ngrok or external URL:
# LLM_URL=https://your-domain.ngrok-free.dev/groq/chat/completions
LLM_TOKEN=your_groq_api_key

# ElevenLabs TTS Configuration (Required)
TTS_VENDOR=elevenlabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL
ELEVENLABS_MODEL_ID=eleven_flash_v2_5

# ARES ASR Configuration (Built-in, no API key needed)
# ARES provides real-time speech recognition optimized for conversational AI

# Modalities Configuration
INPUT_MODALITIES=audio
OUTPUT_MODALITIES=audio

# Server Configuration
PORT=8000
```

### 3. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 4. Test the System

- **API Health**: `GET http://localhost:8000/health`
- **Voice Demo**: `GET http://localhost:8000/realvoice`
- **Start Planning**: `POST http://localhost:8000/agent/invite`

## 📡 Complete API Reference

### Core System Endpoints

- `GET /` - API information and system status
- `GET /health` - Health check endpoint
- `GET /realvoice` - Voice demo interface

### Authentication & Tokens

- `GET /token/` - Generate Agora RTC tokens for client authentication
  - Parameters: `uid`, `channel`
  - Returns: JWT token for voice session with enhanced security

### Conversational AI Agent Management

- `POST /agent/invite` - **Start voice planning session**
  - Creates AI agent with enhanced voice capabilities
  - Configures ARES ASR, ElevenLabs TTS, and Groq LLM with function calling
  - Returns: `agent_id`, `channel_name`, `token`

- `POST /agent/remove` - **End planning session**
  - Auto-saves conversation history with multiple backup mechanisms
  - Generates event summary document (HTML & PDF)
  - Returns: Session summary with file paths and generation status

- `GET /agent/status/{agent_id}` - Get real-time agent status
- `GET /agent/history/{agent_id}` - Get conversation transcript
- `POST /agent/save-conversation/{agent_id}` - Manually save conversation
- `GET /agent/conversations` - List all saved conversations with metadata
- `GET /agent/conversations/{filename}` - Retrieve specific conversation file
- `GET /agent/monitor/{agent_id}` - Monitor agent with real-time status and auto-save
- `POST /agent/webhook/transcript` - Webhook endpoint for real-time transcript capture
- `POST /agent/webhook/agent-status` - Webhook for agent status changes and auto-save triggers
- `GET /agent/auto-save-status` - Get status of auto-save functionality
- `POST /agent/start-auto-save-monitor` - Start background auto-save monitoring
- `GET /agent/debug/config` - Debug endpoint to check agent configuration

### Event Planning Tools (Enhanced Function Calling)

- `POST /groq/chat/completions` - **Main LLM endpoint with enhanced function calling**
  - OpenAI-compatible streaming API with TTS-friendly text cleaning
  - Intelligent query parsing for automatic function selection
  - Integrated venue/vendor search functions with natural language processing
  - Real-time budget estimation with detailed breakdowns
  - Enhanced error handling and fallback mechanisms
  - Supports complex natural language queries with context awareness

- `GET /groq/functions` - List available planning functions with detailed schemas
- `GET /groq/models` - List available LLM models
- `GET /groq/health` - Enhanced LLM service health check with function availability status

### Event Data Management

- `POST /events/create` - Create structured event record
- `GET /events/list` - List all events
- `GET /events/{event_id}` - Get event details
- `PUT /events/{event_id}/rsvp` - Update RSVP status
- `PUT /events/{event_id}/status` - Update event status
- `DELETE /events/{event_id}` - Delete event

### Venue & Vendor Search

- `GET /events/venues/suggestions` - Get venue recommendations
- `GET /events/budget/estimate` - Get budget estimates

### Summary & Reports

- `POST /summary/generate` - Generate event planning summary (HTML & PDF)
- `GET /summary/list` - List generated summaries with metadata
- `GET /summary/{filename}` - Download summary document
- Auto-generation triggered on session end with conversation analysis

## 🎯 Complete User Flow & Usage Examples

### End-to-End Event Planning Flow

#### Step 1: Start Voice Planning Session

```bash
# Generate authentication token
curl "http://localhost:8000/token?uid=12345&channel=wedding-planning-2024"

# Start AI agent for voice conversation
curl -X POST "http://localhost:8000/agent/invite" \
  -H "Content-Type: application/json" \
  -d '{
    "requester_id": "12345",
    "channel_name": "wedding-planning-2024"
  }'
```

**Response:**
```json
{
  "agent_id": "A42AK28VT35RL33FE63RT24KF87DV36X",
  "channel_name": "wedding-planning-2024",
  "token": "jwt_token_here",
  "status": "active"
}
```

#### Step 2: Voice Conversation Examples

**User speaks:** *"Hi, I'm planning a wedding in Delhi for 200 people with a budget of 5 lakh rupees"*

**AI Response:** *"Hello! I'd be happy to help you plan your wedding in Delhi for 200 guests with a budget of 5 lakh rupees. Let me search for suitable venues for you..."*

**Behind the scenes:** The enhanced AI automatically:
1. Parses the natural language query using intelligent text analysis
2. Extracts key parameters: city="delhi", capacity=200, budget_max=500000, event_type="wedding"
3. Calls multiple functions simultaneously:
   - `search_venues(city="delhi", capacity=200, budget_max=500000, event_type="wedding")`
   - `estimate_budget(event_type="wedding", guest_count=200, city="delhi")`
   - `search_vendors(city="delhi", vendor_type="food", budget_max=150000)`
4. Processes and formats results for natural conversation

**AI continues:** *"I found some excellent venues for your wedding. The Grand Ballroom in Connaught Place can accommodate 250 people for Rupees 80,000, and the Royal Garden in Karol Bagh seats 200 for Rupees 60,000. For catering, I recommend Spice Garden Caterers who specialize in wedding cuisine for Rupees 25,000 to 40,000. Would you like more details about these venues or shall we discuss photography and decoration options?"*

#### Step 3: Get Detailed Recommendations

**User speaks:** *"Tell me more about photographers and decorators in Delhi"*

**AI automatically searches and responds:** *"For photography, I recommend Capture Moments Studio in Lajpat Nagar with 4.8 stars, specializing in weddings for 25,000-40,000 rupees. For decoration, Elegant Events in CP offers complete wedding decor for 35,000-50,000 rupees..."*

#### Step 4: End Session & Get Summary

```bash
# End the planning session
curl -X POST "http://localhost:8000/agent/remove" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "A42AK28VT35RL33FE63RT24KF87DV36X"}'
```

**Response:**
```json
{
  "success": true,
  "conversation_auto_saved": true,
  "summary_generated": true,
  "summary_filename": "event_summary_A42AK28VT35RL33FE63RT24KF87DV36X_20241114_123456.pdf",
  "summary_url": "/event-summaries/event_summary_A42AK28VT35RL33FE63RT24KF87DV36X_20241114_123456.pdf",
  "conversation_file": "conversation_A42AK28VT35RL33FE63RT24KF87DV36X_20241114_123456.json",
  "total_messages": 12,
  "session_duration": "8 minutes"
}
```

### Direct API Usage Examples

#### Search Venues Programmatically

```bash
# Search wedding venues in Mumbai for 150 people
curl -X POST "http://localhost:8000/groq/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [
      {"role": "user", "content": "Find wedding venues in Mumbai for 150 people under 3 lakh budget"}
    ],
    "stream": true
  }'
```

#### Get Budget Estimate

```bash
# Get detailed budget breakdown
curl -X POST "http://localhost:8000/groq/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [
      {"role": "user", "content": "What would be the budget for a corporate event in Bangalore for 100 people?"}
    ],
    "stream": true
  }'
```

## 🗣 Enhanced Conversation Flow

The AI assistant follows this intelligent conversation pattern with enhanced function calling:

### Phase 1: Initial Discovery (0-2 minutes)
1. **Greeting & Language**: "Hello! I'm EventMaster Pro. How may I assist you with your event planning needs today?"
2. **Event Type Identification**: "What type of event are you planning?"
3. **Basic Requirements**: "How many people will attend?"
4. **Location Preference**: "Which city are you considering?"

### Phase 2: Intelligent Search & Recommendations (2-5 minutes)
5. **Automatic Function Calling**: AI intelligently parses user input and calls multiple functions:
   - `search_venues()` with extracted criteria
   - `estimate_budget()` for cost planning
   - `search_vendors()` for relevant service providers
6. **Real-time Results**: Provides actual venue names, addresses, pricing, and ratings
7. **Budget Analysis**: Detailed breakdown with city-specific pricing
8. **Vendor Ecosystem**: Comprehensive recommendations for photographers, caterers, decorators

### Phase 3: Detailed Planning (5-10 minutes)
9. **Venue Deep Dive**: Discusses specific venues with amenities and availability
10. **Vendor Coordination**: Provides contact details and service comparisons
11. **Budget Optimization**: AI suggests cost-saving alternatives based on data analysis
12. **Timeline Planning**: Discusses booking priorities and deadlines
13. **Enhanced Recommendations**: Uses `get_recommendations()` for complex queries

### Phase 4: Summary & Next Steps (1-2 minutes)
14. **Comprehensive Recap**: Summarizes all venues, vendors, and budget details
15. **Action Items**: Provides prioritized next steps with contact information
16. **Auto-Documentation**: Generates professional HTML & PDF summaries
17. **Conversation Backup**: Multiple auto-save mechanisms ensure no data loss

## 🎉 Supported Event Types

### Primary Events (Full Database Support)
- **Weddings** (1000+ venues, 500+ vendors)
- **Corporate Events** (Conference halls, hotels, catering)
- **Birthday Parties** (Restaurants, halls, entertainment)
- **Anniversaries** (Intimate venues, special packages)
- **Engagements** (Banquet halls, photography specialists)

### Secondary Events (Basic Support)
- Family Gatherings
- Community Events
- Group Outings
- Religious Ceremonies
- Product Launches

## 🏗 System Architecture & Data Flow

### Enhanced System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │    │   FastAPI        │    │   Agora         │
│   (Web/Mobile)  │◄──►│   Backend        │◄──►│   Conversational│
│                 │    │   + Enhanced     │    │   AI Engine     │
│                 │    │   Function       │    │   + ARES ASR    │
│                 │    │   Calling        │    │   + Webhooks    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Groq LLM       │
                       │   (Llama 3.1)    │
                       │   + Enhanced     │
                       │   Function Tools │
                       │   + Query Parser │
                       └──────────────────┘
                              │
                       ┌──────────────────┐
                       │   ElevenLabs     │
                       │   TTS (Indian)   │
                       │   + Text Cleaning│
                       └──────────────────┘
                              │
                       ┌──────────────────┐
                       │   Event Database │
                       │   (JSON + Search)│
                       │   + Auto-Save    │
                       │   + Summaries    │
                       └──────────────────┘
```

### Detailed Data Flow

#### 1. Voice Input Processing
```
User Speech → ARES ASR → Text Transcript → FastAPI → Groq LLM
```

#### 2. Function Calling Flow
```
User Query → LLM Analysis → Function Selection → Event Tools → Database Search → Results
```

#### 3. Response Generation
```
Search Results → LLM Processing → Natural Response → ElevenLabs TTS → Voice Output
```

#### 4. Session Management
```
Conversation → Auto-Save → Summary Generation → HTML Report → File Storage
```

### Core Components

#### FastAPI Backend (`main.py`)
- **Enhanced Routes**: Agent, Events, Groq LLM, Token, Summary with improved error handling
- **Middleware**: CORS, Static files with security enhancements
- **Health Checks**: Comprehensive system status monitoring
- **Demo Endpoints**: Multiple demo interfaces for testing

#### Enhanced Conversational AI Agent (`routes/agent.py`)
- **Advanced Session Management**: Create/remove voice agents with enhanced configuration
- **Multi-layer Auto-Save**: Webhooks, background monitoring, manual triggers
- **ARES ASR Integration**: Simplified configuration with built-in speech recognition
- **Conversation Tracking**: Local storage, file backup, and real-time monitoring
- **Webhook Handlers**: Real-time transcript capture and status change processing
- **Debug Endpoints**: Configuration validation and troubleshooting tools

#### Enhanced LLM Service (`routes/groq_llm.py`)
- **OpenAI Compatibility**: Standard chat completions API with streaming
- **Intelligent Function Calling**: Automatic query parsing and function selection
- **TTS Optimization**: Text cleaning for better speech synthesis
- **Enhanced Error Handling**: Graceful fallbacks and detailed logging
- **Natural Language Processing**: Context-aware function parameter extraction

#### Advanced Event Tools (`event_tools.py`)
- **Decorated Functions**: LLM-compatible function definitions with schemas
- **Enhanced Venue Search**: `search_venues()` with intelligent filtering
- **Comprehensive Vendor Search**: `search_vendors()` by category with speciality matching
- **Detailed Budget Estimation**: `estimate_budget()` with city-specific pricing and breakdowns
- **Smart Recommendations**: `get_recommendations()` with natural language query processing
- **Location Services**: `get_cities_and_areas()` for geographic data

#### Search Engine (`event_search.py`)
- **Advanced Data Processing**: JSON database queries with enhanced filtering
- **Multi-criteria Search**: Complex filtering with ranking algorithms
- **Intelligent Matching**: Rating-based sorting with relevance scoring
- **Budget Analysis**: Advanced price parsing and range extraction

#### Enhanced Summary Generator (`event_summary.py`)
- **Intelligent Conversation Analysis**: Extract event details with NLP
- **Advanced Visualizations**: Matplotlib charts and budget breakdowns
- **Multi-format Generation**: HTML & PDF professional reports
- **Organized File Management**: Structured storage with metadata

## 📁 Complete Project Structure

```
gdg-hackathon-14-11-25/
├── main.py                          # Enhanced FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables configuration
├── system_prompt.txt               # AI assistant system prompt (multilingual)
├── README.md                       # This comprehensive documentation
├── ARES_ASR_MIGRATION.md          # ARES ASR migration documentation
├── key_and_secret.txt             # API credentials reference
│
├── class_types/                    # Data models and type definitions
│   └── agora_types.py             # Enhanced Pydantic models for API requests/responses
│
├── routes/                         # Enhanced API route handlers
│   ├── agent.py                   # Enhanced conversational AI agent with auto-save
│   ├── token.py                   # Agora RTC token generation
│   ├── events.py                  # Event CRUD operations
│   ├── groq_llm.py               # Enhanced Groq LLM with intelligent function calling
│   ├── bedrock_llm.py            # AWS Bedrock LLM integration (alternative)
│   └── summary.py                 # Enhanced event summary generation (HTML & PDF)
│
├── components/                     # Utility components
│   ├── speech_to_text_transcript.py # Speech processing utilities
│   └── test_llm.py               # LLM testing utilities
│
├── static/                        # Web interface files
│   ├── real-voice.html           # Enhanced voice demo interface
│   └── test-download.html        # Download testing page
│
├── conversations/                 # Auto-saved conversation transcripts
│   ├── conversation_*.json       # Individual conversation files with metadata
│   └── .gitkeep                  # Directory placeholder
│
├── event_summaries/              # Generated planning summaries
│   ├── event_summary_*.html      # Professional HTML reports
│   ├── event_summary_*.pdf       # Professional PDF reports
│   └── (auto-generated files)    # Budget charts and visualizations
│
├── references/                   # Documentation and guides
│   ├── deepgram-docs/           # ASR integration guides
│   ├── Agora API references     # Conversational AI documentation
│   └── Integration guides       # Setup and configuration help
│
├── original_codes/              # Backup of original implementations
│   ├── original_main.py         # Original main application
│   ├── original_agent.py        # Original agent implementation
│   ├── original_groq_llm.py     # Original LLM service
│   └── (other backup files)     # Previous versions for reference
│
├── Core Event Planning Files:
├── event_data.json             # Complete venue/vendor database (1000+ entries)
├── event_search.py             # Enhanced search engine with filtering and ranking
├── event_tools.py              # Enhanced function calling tools with decorators
├── event_summary.py            # Enhanced summary generation (HTML & PDF)
│
├── Testing & Utilities:
├── test_full_pipeline.py       # End-to-end system testing
├── test_function_calling.py    # Enhanced function calling validation
├── test_summary.py             # Summary generation testing
├── test_extraction.py          # Data extraction testing
├── demo_voice_bot.py           # Voice bot demonstration
└── client_example.html         # Client integration example
```

## 🔧 Development Guide

### Adding New Cities/Venues

1. **Update Event Database** (`event_data.json`):
```json
{
  "cities": {
    "new_city": {
      "name": "New City",
      "areas": {
        "area_name": {
          "name": "Area Name",
          "venues": [...],
          "vendors": {...}
        }
      }
    }
  }
}
```

2. **Update Search Engine** (`event_search.py`):
   - Add city to multipliers
   - Update area mappings
   - Test search functionality

### Adding New Event Types

1. **Update System Prompt** (`system_prompt.txt`):
   - Add event type to `<VenueSuggestionsByEventType>`
   - Update conversation flow examples

2. **Update Budget Calculations** (`event_search.py`):
   - Add base costs for new event type
   - Update vendor category mappings

3. **Update Function Tools** (`event_tools.py`):
   - Add event type to enum lists
   - Update function descriptions

### Adding New LLM Providers

1. **Create New Route** (`routes/new_llm.py`):
```python
from fastapi import APIRouter
router = APIRouter(prefix="/new-llm", tags=["new-llm"])

@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Implement OpenAI-compatible endpoint with function calling support
    # Include TTS-friendly text cleaning
    # Add enhanced error handling
    pass
```

2. **Update Agent Configuration** (`routes/agent.py`):
   - Add new LLM URL option to environment configuration
   - Update system prompt handling for enhanced function calling
   - Ensure webhook compatibility for conversation tracking

### Adding New Vendor Categories

1. **Update Event Tools** (`event_tools.py`):
   - Add to vendor_type enum
   - Update search functions

2. **Update Database** (`event_data.json`):
   - Add vendor category to areas
   - Populate with vendor data

3. **Update System Prompt** (`system_prompt.txt`):
   - Add vendor keywords
   - Update conversation examples

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Agent Creation Fails
**Symptoms**: `POST /agent/invite` returns 500 error

**Solutions**:
```bash
# Check Agora credentials
echo $AGORA_APP_ID
echo $AGORA_CUSTOMER_ID

# Verify API endpoint
curl -X GET "http://localhost:8000/agent/debug/config"

# Test token generation
curl "http://localhost:8000/token?uid=12345&channel=test"
```

#### 2. No Voice Response
**Symptoms**: Agent starts but doesn't speak

**Solutions**:
- **Check ElevenLabs API Key**: Verify in `.env` file
- **Verify TTS Vendor**: Ensure `TTS_VENDOR=elevenlabs` is set
- **Test TTS Endpoint**: 
```bash
curl -X POST "http://localhost:8000/agent/{agent_id}/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}'
```
- **Voice ID Issues**: Use `EXAVITQu4vr4xnSDxMaL` for Indian English
- **Model Configuration**: Verify `ELEVENLABS_MODEL_ID=eleven_flash_v2_5`

#### 3. Speech Recognition Problems
**Symptoms**: User speech not recognized

**Solutions**:
- **ARES ASR is Built-in**: No API key needed
- **Check Audio Input**: Ensure microphone permissions
- **Network Issues**: Verify Agora connectivity
- **Debug Transcripts**: Check console logs for speech-to-text output

#### 4. Function Calling Not Working
**Symptoms**: AI doesn't provide venue/vendor recommendations

**Solutions**:
```bash
# Check event data file
ls -la event_data.json

# Test enhanced function calling
curl -X GET "http://localhost:8000/groq/functions"

# Verify Groq API key and LLM URL
echo $GROQ_API_KEY
echo $LLM_URL

# Test function calling with natural language
curl -X POST "http://localhost:8000/groq/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [
      {"role": "user", "content": "Find wedding venues in Delhi for 100 people"}
    ],
    "stream": true
  }'
```

#### 5. Summary Generation Fails
**Symptoms**: No HTML summary created after session

**Solutions**:
```bash
# Check dependencies
pip install matplotlib reportlab

# Verify output directory
ls -la event_summaries/

# Test summary generation
curl -X POST "http://localhost:8000/summary/generate" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "test"}'
```

### Debug Endpoints

- `GET /agent/debug/config` - Check all configuration including ARES ASR setup
- `GET /groq/health` - Verify LLM service and function calling availability
- `GET /agent/auto-save-status` - Check conversation tracking and webhook status
- `GET /agent/conversations` - List saved conversations with metadata
- `GET /agent/monitor/{agent_id}` - Real-time agent monitoring with auto-save
- `POST /agent/webhook/transcript` - Test transcript webhook
- `POST /agent/webhook/agent-status` - Test status change webhook

### Log Analysis

**Important Log Patterns**:
```bash
# Successful agent creation with ARES ASR
"✅ Agent created successfully with ARES ASR configuration"
"🎤 Audio will be processed by ARES ASR with low latency"

# Enhanced function calling
"🔧 DEBUG: Executing 2 function calls"
"✅ Function search_venues executed successfully"
"🔧 DEBUG: Intelligent query parsing detected: venue search"

# Voice processing and transcription
"🎤 USER TRANSCRIPT: 'I need a wedding venue in Delhi'"
"🤖 GROQ LLM REQUEST RECEIVED!"
"📝 Messages count: 3, Tools available: True"

# Enhanced auto-save system
"💾 Conversation automatically saved to: conversations/..."
"📊 Generating event summary for agent..."
"✅ Auto-saved conversation for inactive agent"
"🎯 Found inactive agent with status: idle"

# Webhook processing
"🎤 TRANSCRIPT WEBHOOK TRIGGERED!"
"🤖 AGENT STATUS WEBHOOK TRIGGERED!"
"💾 Auto-saving conversation due to agent_idle"
```

### Performance Optimization

1. **Reduce Response Time**:
   - Use `llama-3.1-8b-instant` model for faster inference
   - Set `max_tokens: 150` for quicker responses
   - Enable streaming: `stream: true` (required for Agora)
   - Implement intelligent function call batching

2. **Improve Voice Quality**:
   - Use `eleven_flash_v2_5` model for optimal speed/quality balance
   - Set `sample_rate: 24000` for clarity
   - Configure proper voice activity detection
   - Enable TTS-friendly text cleaning for better pronunciation

3. **Enhanced Database Performance**:
   - Keep `event_data.json` optimized and under 5MB
   - Use intelligent search algorithms with relevance scoring
   - Cache frequent queries and function call results
   - Implement background data preprocessing

4. **Conversation Management**:
   - Use efficient auto-save mechanisms with background processing
   - Implement conversation compression for large sessions
   - Optimize webhook processing for real-time updates

## 📊 System Monitoring

### Health Checks
```bash
# Overall system health
curl http://localhost:8000/health

# LLM service health
curl http://localhost:8000/groq/health

# Agent status
curl http://localhost:8000/agent/auto-save-status
```

### Performance Metrics
- **Response Time**: < 2 seconds for enhanced venue search with function calling
- **Voice Latency**: < 500ms with ARES ASR (optimized for conversational AI)
- **Function Calls**: < 1 second for complex database queries with intelligent parsing
- **Summary Generation**: < 5 seconds for HTML report, < 10 seconds for PDF with charts
- **Auto-save Processing**: < 2 seconds for conversation backup
- **Webhook Response**: < 100ms for real-time transcript capture

## 🎯 Production Deployment

### Environment Setup
```bash
# Production environment variables
export AGORA_APP_ID="your_production_app_id"
export AGORA_APP_CERTIFICATE="your_production_app_certificate"
export AGORA_CUSTOMER_ID="your_production_customer_id"
export AGORA_CUSTOMER_SECRET="your_production_customer_secret"
export GROQ_API_KEY="your_production_groq_key"
export ELEVENLABS_API_KEY="your_production_elevenlabs_key"
export TTS_VENDOR="elevenlabs"
export LLM_URL="https://your-domain.com/groq/chat/completions"

# Start with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Security Considerations
- **API Keys**: Use environment variables, never commit to code
- **CORS**: Configure specific origins for production
- **Rate Limiting**: Implement request throttling
- **Authentication**: Add user authentication for production use

## 📄 License & Credits

This project is created for the **GDG Hackathon** and is available for educational and demonstration purposes.

### Technologies Used
- **Agora Conversational AI Engine** - Real-time voice communication
- **Groq** - High-performance LLM inference
- **ElevenLabs** - Natural text-to-speech
- **FastAPI** - Modern Python web framework
- **ReportLab & Matplotlib** - Professional document generation

### Data Sources
- Venue and vendor data compiled from public sources
- Pricing information based on market research
- City-specific multipliers from industry standards

---

**Built with ❤️ for the GDG Developer Community**

*For questions, issues, or contributions, please refer to the troubleshooting guide above or check the conversation logs for detailed error information.*
