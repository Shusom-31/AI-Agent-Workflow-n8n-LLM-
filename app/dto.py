from pydantic import BaseModel
from typing import Dict


class LeadRequest(BaseModel):
    """Request model for lead messages"""
    message: str


class LeadResponse(BaseModel):
    """Response model with classification and reply"""
    classification: Dict
    reply: str
