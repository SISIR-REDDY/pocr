"""
Verification route: verifies submitted fields against extracted fields.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging

import sys
import os

# Add parent directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from services.verifier import verify_fields

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/verify", tags=["verify"])


class VerifyRequest(BaseModel):
    submitted_fields: Dict[str, Optional[str]]  # Allow None values
    extracted_fields: Dict[str, Optional[str]]


@router.post("")
async def verify_submission(request: VerifyRequest):
    """
    Verify submitted fields against extracted fields.
    
    Args:
        request: Contains submitted_fields and extracted_fields
        
    Returns:
        Verification results with match scores and mismatches
    """
    try:
        logger.info(f"[VERIFY] Received verification request")
        logger.info(f"[VERIFY] Submitted fields: {list(request.submitted_fields.keys())}")
        logger.info(f"[VERIFY] Extracted fields: {list(request.extracted_fields.keys())}")
        
        result = verify_fields(
            request.submitted_fields,
            request.extracted_fields
        )
        
        logger.info(f"[VERIFY] Verification complete. Overall score: {result.get('overall_score', 0.0):.2f}")
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

