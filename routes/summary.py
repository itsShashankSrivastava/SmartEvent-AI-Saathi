"""
Event Summary API Routes
Provides endpoints for generating, viewing, and downloading event summaries
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, Optional
from pydantic import BaseModel
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from event_summary import generate_event_summary, summary_generator
    SUMMARY_AVAILABLE = True
    print("✅ Event summary system loaded successfully")
except ImportError as e:
    SUMMARY_AVAILABLE = False
    print(f"⚠️ Event summary system not available: {e}")

router = APIRouter(prefix="/summary", tags=["summary"])

class SummaryRequest(BaseModel):
    agent_id: str
    conversation_data: Optional[Dict] = None

@router.post("/generate")
async def generate_summary(request: SummaryRequest):
    """Generate event summary from conversation data"""
    if not SUMMARY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Summary generation not available")
    
    try:
        # If conversation_data not provided, try to load from saved conversations
        conversation_data = request.conversation_data
        
        if not conversation_data:
            # Try to load from conversations directory
            conversations_dir = Path("conversations")
            conversation_files = list(conversations_dir.glob(f"conversation_{request.agent_id}_*.json"))
            
            if conversation_files:
                # Get the most recent conversation file
                latest_file = max(conversation_files, key=lambda x: x.stat().st_mtime)
                
                import json
                with open(latest_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
            else:
                raise HTTPException(status_code=404, detail="No conversation data found for this agent")
        
        # Generate summary
        result = generate_event_summary(conversation_data)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Event summary generated successfully",
                "summary_url": result["url"],
                "filename": result["filename"],
                "event_details": result["event_details"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Summary generation failed: {result['error']}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")

@router.get("/view/{filename}")
async def view_summary(filename: str):
    """View event summary HTML document"""
    try:
        summaries_dir = Path("event_summaries")
        file_path = summaries_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Summary file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error viewing summary: {str(e)}")

@router.get("/download/{filename}")
async def download_summary(filename: str):
    """Download event summary as PDF or HTML file"""
    try:
        summaries_dir = Path("event_summaries")
        file_path = summaries_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Summary file not found")
        
        # Determine media type based on file extension
        if filename.endswith('.pdf'):
            media_type = 'application/pdf'
        else:
            media_type = 'text/html'
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading summary: {str(e)}")

@router.get("/list")
async def list_summaries():
    """List all available event summaries"""
    try:
        summaries_dir = Path("event_summaries")
        if not summaries_dir.exists():
            return {"summaries": [], "total": 0}
        
        summaries = []
        for file_path in summaries_dir.glob("event_summary_*.html"):
            try:
                stat = file_path.stat()
                
                # Extract agent_id from filename
                filename_parts = file_path.stem.split('_')
                agent_id = filename_parts[2] if len(filename_parts) > 2 else "unknown"
                
                summaries.append({
                    "filename": file_path.name,
                    "agent_id": agent_id,
                    "created": stat.st_ctime,
                    "size_bytes": stat.st_size,
                    "view_url": f"/summary/view/{file_path.name}",
                    "download_url": f"/summary/download/{file_path.name}"
                })
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        # Sort by creation time (newest first)
        summaries.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "summaries": summaries,
            "total": len(summaries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing summaries: {str(e)}")

@router.post("/generate-from-agent/{agent_id}")
async def generate_summary_from_agent(agent_id: str):
    """Generate summary directly from agent ID (convenience endpoint)"""
    return await generate_summary(SummaryRequest(agent_id=agent_id))

@router.get("/agent/{agent_id}")
async def get_agent_summaries(agent_id: str):
    """Get all summaries for a specific agent"""
    try:
        summaries_dir = Path("event_summaries")
        if not summaries_dir.exists():
            return {"summaries": [], "total": 0}
        
        agent_summaries = []
        for file_path in summaries_dir.glob(f"event_summary_{agent_id}_*.html"):
            try:
                stat = file_path.stat()
                agent_summaries.append({
                    "filename": file_path.name,
                    "agent_id": agent_id,
                    "created": stat.st_ctime,
                    "size_bytes": stat.st_size,
                    "view_url": f"/summary/view/{file_path.name}",
                    "download_url": f"/summary/download/{file_path.name}"
                })
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        # Sort by creation time (newest first)
        agent_summaries.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "agent_id": agent_id,
            "summaries": agent_summaries,
            "total": len(agent_summaries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent summaries: {str(e)}")

@router.delete("/{filename}")
async def delete_summary(filename: str):
    """Delete an event summary file"""
    try:
        summaries_dir = Path("event_summaries")
        file_path = summaries_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Summary file not found")
        
        file_path.unlink()
        
        return {
            "success": True,
            "message": f"Summary {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting summary: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for summary service"""
    return {
        "status": "healthy" if SUMMARY_AVAILABLE else "unavailable",
        "summary_generation": SUMMARY_AVAILABLE,
        "dependencies": {
            "matplotlib": "available" if SUMMARY_AVAILABLE else "missing",
            "reportlab": "available" if SUMMARY_AVAILABLE else "missing"
        }
    }