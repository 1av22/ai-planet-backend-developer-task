import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import openai  # Replace Gemini with OpenAI or another compatible model
from pydantic import BaseModel
from fastapi import APIRouter, Depends
import httpx

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter(
    prefix='/rag',
    tags=['rag']
)

# Set up OpenAI API client instead of Google Gemini
openai.api_key = OPENAI_API_KEY


async def get_user_info_from_api():
    """
    Fetch the current user data by calling the /auth/me endpoint.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/auth/me")
        if response.status_code == 200:
            return response.json()  # {'username': username, 'id': user_id}
        else:
            raise HTTPException(
                status_code=401, detail="User not authenticated")


def write_to_file_safe(filename, data):
    """
    Write data to a file without locking. 
    If you need thread-safe writing, use other methods like queue or multiprocessing.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(data)


# Function to initialize the chat engine for each request
async def create_chat_engine(user_id: int):
    """
    Create and return a chat engine for the user.
    In this case, we replace Gemini model with OpenAI API or another compatible solution.
    """
    # Define the user's data folder path dynamically
    user_folder = f"data/{user_id}"

    # Check if the folder exists, raise error if not
    if not os.path.exists(user_folder):
        raise HTTPException(
            status_code=404, detail=f"User folder {user_folder} not found.")

    # Check for the vector store file in the user folder
    vector_store_path = os.path.join(user_folder, "vector_store")

    if not os.path.exists(vector_store_path):
        raise HTTPException(
            status_code=404, detail="Vector store not found. Ensure the file has been processed and indexed.")

    # Normally, load the vector store from disk or other methods

    # Here we are simulating the chat engine initialization with OpenAI API
    # OpenAI API setup can vary, here's an example for completion-based chat
    def chat_engine(input_data: str):
        response = openai.Completion.create(
            model="text-davinci-003",  # Choose a model
            prompt=input_data,
            max_tokens=150
        )
        return response.choices[0].text.strip()

    return chat_engine


class QueryRequest(BaseModel):
    input_data: str


# POST endpoint for the chat query
@router.post("/chat")
async def get_chat_response(request: QueryRequest):
    user_info = await get_user_info_from_api()
    user_id = user_info.get("id")

    # Create the chat engine for the user
    chat_engine = await create_chat_engine(user_id)

    input_data = request.input_data
    try:
        # Read the previous chat history (optional)
        previous_history = ""
        with open("res.txt", "r", encoding="utf-8") as f:
            previous_history = f.read()

        # Define the system prompt based on the input data and previous chat history
        system_prompt = f"""
        Hey you are a RAG bot that answers questions only from the given context. This is the previous history:
        {previous_history}.
        Now answer this query: {input_data}
        """

        # Get the response from the chat engine based on the system prompt
        response = chat_engine(system_prompt)

        # Save the chat history to file for future context
        with open("res.txt", "a", encoding="utf-8") as f:
            f.write(f"UserQuery \n{input_data}\n")
            f.write(f"Response\n{response}\n")

        return JSONResponse(content={"message": response}, status_code=200)

    except Exception as e:
        # Handle any errors during processing
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}")
