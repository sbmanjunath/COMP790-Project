from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os

import requests
import json

from google import genai

from prompts import (
    get_alternate_backstory_prompt, 
    alternate_guilty_prompt,
    get_ground_truth_prompt,
    alternate_innocent_prompt
)

user_data = {}

# Initialize FastAPI app
app = FastAPI()

# Replace with your Google Gemini API key
API_KEY = "UPDATE_API_KEY"
os.environ["GEMINI_API_KEY"] = API_KEY
client = genai.Client(api_key=API_KEY)

def call_gemini(prompt: str, model: str="2.0-flash"):
    headers = {
        "Content-Type": "application/json"
    }
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-{model}:generateContent?key={API_KEY}"

    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            response_json = response.json()
            # Debugging: Print API response to inspect structure
            # print(json.dumps(response_json, indent=2))

            # Extract response safely
            if "candidates" in response_json and response_json["candidates"]:
                return response_json["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "Error: API response is missing expected data."
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return f"Error: Unexpected response format - {str(e)}"
    else:
        return f"Error: {response.status_code}, {response.text}"
    

def parse_llm_into_scenario(llm_response):
    response_alt = llm_response.replace("\n", "")
    response_alt = response_alt.replace("```json", '"')
    response_alt = response_alt.replace("```", "")
    response_alt = response_alt[1:]
    questions = json.loads(response_alt)

    return questions

# ---- Request Models ----
class StoryRequest(BaseModel):
    difficulty: int
    setting: str  # "supermarket", "movie theater", "swimming pool", etc
    murder_mode: str    # "poison", "stabbing", "shooting", etc

class Characters(BaseModel):
    name: str
    description: str

class StoryResponse(BaseModel):
    user_id: int
    background: str
    characters: list[Characters]


class GroundTruth(BaseModel):
    killer: str
    method: str
    motive: str
    timeline: List[str]
    clues: Any

class ConversationRequest(BaseModel):
    user_id: int
    character: str
    question: str

class StoryDetails():
    background: str
    characters: List[Dict[str, str]]
    ground_truth: Dict[str, Any]

    def __init__(self, background):
        self.background = background['background']
        self.characters = background['characters']
    
    def set_ground_truth(self, ground_truth):
        self.ground_truth = ground_truth
    

# ---- Endpoints ----

@app.post("/story/generate")
def generate_story(request: StoryRequest) -> StoryResponse:
    """Generates a story using Gemini 2.0 Flash"""
    
    num_users = len(user_data) + 1
    user_data[num_users] = {"difficulty": request.difficulty, "setting": request.setting, "mode": request.murder_mode}

    user_data[num_users]["history"] = []
    
    try:
        story_prompt = get_alternate_backstory_prompt(request.difficulty, request.setting, request.murder_mode)
        response = call_gemini(story_prompt)
        response = parse_llm_into_scenario(response)

        user_data[num_users]["data"] = StoryDetails(response)
        return {
            "user_id": num_users,
            "background": response["background"], 
            "characters": response["characters"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/story/ground_truth")
def get_ground_truth(user_id: int) -> GroundTruth:
    """Generates the ground truth of the story: the killer, the motive, the method, the clues and the timeline"""

    if user_id not in user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = user_data[user_id]["data"]

    try:
        ground_truth_prompt = get_ground_truth_prompt(data.background, data.characters)
        ground_truth = call_gemini(ground_truth_prompt, model="2.5-flash-preview-04-17")
        ground_truth = parse_llm_into_scenario(ground_truth)

        user_data[user_id]["data"].set_ground_truth(ground_truth)

        return ground_truth
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation")
async def chat(request: ConversationRequest) -> str:
    """Simulates the conversation"""
    user_id = request.user_id
    if user_id not in user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = user_data[user_id]["data"]
    
    character_name = request.character
    question = request.question
    
    history = user_data[user_id]["history"]
    character = [ch for ch in data.characters if ch["name"] == character_name]
    background = {"background": data.background, "characters": data.characters}

    try:
        if character_name == data.ground_truth["killer"]:
            chat_prompt = alternate_guilty_prompt(question, character[0], background, data.ground_truth, history)
        else:
            chat_prompt = alternate_innocent_prompt(question, character[0], background, data.ground_truth, history)

        print(chat_prompt)

        response = call_gemini(chat_prompt)
        history.append({"character": character_name, "question": question, "answer": response})
    
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # ---- Run the Server ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
