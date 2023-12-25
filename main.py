from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()  # Load environment variables from .env file

# Initialize OpenAI client
client = openai.Client(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Define Pydantic model for chat message
class ChatMessage(BaseModel):
    message: str

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Define the chat endpoint
@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": chat_message.message,
                }
            ],
            model="gpt-3.5-turbo",
        )
        response_content = chat_completion.choices[0].message.content
        return {"response": response_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


