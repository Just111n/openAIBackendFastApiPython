from fastapi import FastAPI, HTTPException,Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

# @app.post("/chat-stream")
# async def chat(chat_message: ChatMessage):
#     try:
#         stream = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": chat_message.message}],
#             stream=True,
#         )
#         for chunk in stream:
#             print(chunk.choices[0].delta.content or "", end="\n")
#     except Exception as e:
#         print(e)

#     # return Response(event_generator(), media_type="text/event-stream")
    
@app.post("/chat-stream")
async def chat(chat_message: ChatMessage):
    async def event_generator():
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": chat_message.message}],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

