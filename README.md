# **README – AI Agent Workflow Automation**

## **Project Overview**

This project demonstrates an AI-driven automation workflow for handling incoming leads using **n8n** workflow automation and **FastAPI** as a backend endpoint.

The workflow:

* Accepts lead messages via a **webhook endpoint**.
* Uses an **LLM (Google Gemini / PaLM)** to:
  * Classify the intent (**Sales / Support / Spam**)
  * Extract key fields: **name, company, requirement**
* Sends an **AI-generated automated response**.
* Provides **logging, error handling, and fallback logic**.
* Supports **Swagger UI** for testing the endpoint.

---

## **Tech Stack**

* **Workflow Automation:** n8n
* **Backend / API:** Python 3.11+, FastAPI
* **LLM Integration:** Google Gemini Chat Model (via n8n)
* **Database:** PostgreSQL 
* **Logger:** Python `logging` module
* **Environment Variables:** `.env` for secure configuration

---

## **Project Structure**

```
ai-lead-workflow/
│
├── app/
│   ├── main.py           # FastAPI endpoint
│   ├── dto.py            # Request / Response DTOs
│   └── logger.py         # Logger setup
│
├── .env                  # Environment variables (N8N_WEBHOOK_URL)
├── requirements.txt      # Python dependencies
├── n8n-workflow.json     # n8n exported workflow
└── README.md             # Project documentation
```

---

## **Setup Instructions**

### **1. Install Python dependencies**

```bash
pip install fastapi uvicorn httpx python-dotenv pydantic
```

### **2. Create `.env` file**

```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/lead
```

### **3. Run FastAPI**

```bash
uvicorn app.main:app --reload
```

Swagger UI will be available at:

```
http://127.0.0.1:8000/docs
```

---

## **n8n Workflow**

* Webhook Node receives lead requests from FastAPI endpoint.
* Code Node generates LLM prompt with `message` + `requirement`.
* Basic LLM Chain Node sends prompt to **Google Gemini Chat Model**.
* Code Node parses LLM response into JSON: `{ intent, name, company, requirement }`.
* Response returned to FastAPI with `classification` and `reply`.
* PostgreSQL Node is used to store lead data in the database table lead.

---

## **Prompt Strategy**

* The prompt instructs the LLM to **return only valid JSON** with keys:

  ```json
  {
    "intent": "Sales | Support | Spam",
    "name": "",
    "company": "",
    "requirement": ""
  }
  ```
* This ensures **structured output** for automated handling.

**Example Prompt:**

```
Return ONLY valid JSON.

{
  "intent": "Sales | Support | Spam",
  "name": "",
  "company": "",
  "requirement": ""
}

Message: "Hello, I am Shusom from Upscalebd Ltd. I want  AI Engineer"
```

---

## **Error Handling**

* All LLM parsing is wrapped in `try/except` blocks.
* FastAPI endpoint validates request payload via Pydantic DTO.
* Logger tracks errors with **stack trace** for debugging.
* Fallback responses are provided for unknown intents.

---

## **Swagger / Testing**

* The FastAPI endpoint `/lead` accepts POST requests:

```json
{
  "message": "Hello, I am Shusom from Upscalebd Ltd. I want  AI Engineer ",
}
```

* Response:

```json
{
  "classification": {
    "intent": "Sales",
    "name": "Shusom",
    "company": "Upscalebd Ltd.",
    "requirement": "AI Engineer"
  },
  "reply": "Hi Shusom, thanks for your interest! Our sales team will contact you shortly."
}
```

---

## **Hallucination Mitigation**

* Using **structured prompts** to strictly request JSON output.
* Parsing LLM output with regex to remove code blocks ensures correct JSON.
* Unknown or invalid outputs default to `intent: "Unknown"`.

---

## **Notes**

* PostgreSQL is used to persist all lead data, so every lead is securely stored.
* Environment variables manage webhook URLs securely.
* Logger tracks all messages, errors, and responses for audit and debugging.

---

## **License**

MIT License
