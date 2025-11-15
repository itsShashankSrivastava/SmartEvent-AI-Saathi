from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from agora_token_builder import RtcTokenBuilder, RtmTokenBuilder
import os
from datetime import datetime
import random
import string

router = APIRouter(prefix="/token", tags=["token"])

class TokenResponse(BaseModel):
    rtc_token: str
    rtm_token: str
    uid: str
    channel: str

class CombinedTokenResponse(BaseModel):
    token: str  # Combined token with both RTC and RTM privileges
    uid: str
    channel: str

def generate_channel_name() -> str:
    timestamp = int(datetime.now().timestamp())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"event-planning-{timestamp}-{random_str}"

@router.get("/", response_model=TokenResponse)
async def generate_token(
    uid: int = Query(0, description="User ID"),
    channel: str = Query(None, description="Channel name")
):
    """Generate separate RTC and RTM tokens"""
    # Validate environment variables
    if not os.getenv("AGORA_APP_ID") or not os.getenv("AGORA_APP_CERTIFICATE"):
        raise HTTPException(
            status_code=500,
            detail="Agora credentials are not set"
        )

    # Generate channel name if not provided
    channel_name = channel or generate_channel_name()
    expiration_time = int(datetime.now().timestamp()) + 3600

    try:
        # Generate RTC token
        rtc_token = RtcTokenBuilder.buildTokenWithUid(
            appId=os.getenv("AGORA_APP_ID"),
            appCertificate=os.getenv("AGORA_APP_CERTIFICATE"),
            channelName=channel_name,
            uid=uid,
            role=1,
            privilegeExpiredTs=expiration_time
        )
        
        # Generate RTM token
        rtm_token = RtmTokenBuilder.buildToken(
            appId=os.getenv("AGORA_APP_ID"),
            appCertificate=os.getenv("AGORA_APP_CERTIFICATE"),
            userAccount=str(uid),
            role=1,  # Role_Rtm_User
            privilegeExpiredTs=expiration_time
        )
        
        return TokenResponse(
            rtc_token=rtc_token,
            rtm_token=rtm_token,
            uid=str(uid),
            channel=channel_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Agora tokens: {str(e)}"
        )

@router.get("/combined", response_model=CombinedTokenResponse)
async def generate_combined_token(
    uid: int = Query(0, description="User ID"),
    channel: str = Query(None, description="Channel name")
):
    """
    Generate a single token with both RTC and RTM privileges
    This is recommended for Agora Conversational AI agents
    """
    # Validate environment variables
    if not os.getenv("AGORA_APP_ID") or not os.getenv("AGORA_APP_CERTIFICATE"):
        raise HTTPException(
            status_code=500,
            detail="Agora credentials are not set"
        )

    # Generate channel name if not provided
    channel_name = channel or generate_channel_name()
    expiration_time = int(datetime.now().timestamp()) + 3600

    try:
        # Generate RTC token with both RTC and RTM privileges
        # For agents, we use RTC token as the primary token
        token = RtcTokenBuilder.buildTokenWithUid(
            appId=os.getenv("AGORA_APP_ID"),
            appCertificate=os.getenv("AGORA_APP_CERTIFICATE"),
            channelName=channel_name,
            uid=uid,
            role=1,  # Publisher role
            privilegeExpiredTs=expiration_time
        )
        
        return CombinedTokenResponse(
            token=token,
            uid=str(uid),
            channel=channel_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate combined Agora token: {str(e)}"
        )