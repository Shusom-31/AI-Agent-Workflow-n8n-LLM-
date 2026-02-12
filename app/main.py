from fastapi import FastAPI, HTTPException
import os
import httpx
from dotenv import load_dotenv
from app.logger import logger
from app.dto import LeadRequest, LeadResponse

# Load environment variables
load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

app = FastAPI(
    title="AI Lead Endpoint",
    description="Accepts lead messages and calls n8n webhook for automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "AI Lead API is running"}


@app.post("/lead", response_model=LeadResponse)
async def handle_lead(lead: LeadRequest):
    """
    Receives a lead message, sends it to n8n webhook, parses response.
    """
    try:
        logger.info("Received lead message: %s", lead.message)

        if not N8N_WEBHOOK_URL:
            logger.error("N8N_WEBHOOK_URL is not configured")
            raise HTTPException(status_code=500, detail="N8N_WEBHOOK_URL not configured")

        # Call n8n webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(N8N_WEBHOOK_URL, json={"message": lead.message})
            if response.status_code != 200:
                logger.error("n8n webhook failed: %s", response.text)
                raise HTTPException(status_code=500, detail="n8n webhook call failed")

            n8n_data = response.json()
            
            # Handle both list and dict responses from n8n
            if isinstance(n8n_data, list):
                # If n8n returns a list, take the first item
                n8n_data = n8n_data[0] if n8n_data else {}
            
            # Build classification from n8n response fields
            classification = {
                "intent": n8n_data.get("intent", "Unknown"),
                "name": n8n_data.get("name", ""),
                "company": n8n_data.get("company", ""),
                "requirement": n8n_data.get("requirement", ""),
                "created_at": n8n_data.get("created_at", "")
            }
            reply = n8n_data.get("reply", "Thanks for your message.")

        logger.info("Classification: %s", classification)
        logger.info("Reply: %s", reply)

        return LeadResponse(classification=classification, reply=reply)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to process lead")
        raise HTTPException(status_code=500, detail=str(e))
