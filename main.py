import json
from fastapi import FastAPI, Body
import google.generativeai as genai
from typing import List, Dict

app = FastAPI()

# Replace with your actual API key
api_key = ""

with open("api_key.txt", "r") as f:
  api_key = f.read().strip()

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = "You will be given an object containing a list of users with their user id and bio and a list of tasks with task id and its description. Distribute the tasks and respond with your assignments in this format task_id:user_id|task_id:user_id."

model = None  # Initialize model outside the request handler

def generate_distribution(encoded):
  encoded = encoded.strip()
  output = []
  items = encoded.split("|")
  for i in items:
    dist = i.split(":")
    output.append(
        {
            "task_id": int(dist[0]),
            "user_id": int(dist[1])
        }
    )
  return output

@app.post("/distribute_tasks")
async def distribute_tasks(data: Dict = Body(...)):
  """
  API endpoint to distribute tasks based on user information.

  Expects a dictionary containing lists of users and tasks in the following format:

  {
    "users": [
      { "id": 1, "bio": "..." },
      ...
    ],
    "tasks": [
      { "id": 1, "task": "..." },
      ...
    ]
  }
  """

  global model  # Access the global model variable

  if model is None:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)

  history = history=[
  {
    "role": "user",
    "parts": ['''
    
    users:
[
 {
      "id": 1,
      "bio": "Experienced software engineer with expertise in Python and machine learning."
    },
    {
      "id": 2,
      "bio": "Backend developer with experience in working with databases."
    },
    {
      "id": 3,
      "bio": "Full-stack developer proficient in JavaScript frameworks."
    },
    {
      "id": 4,
      "bio": "Data scientist specializing in statistical modeling and analysis."
    },
    {
      "id": 5,
      "bio": "UI/UX designer with a focus on user-centered design principles."
    }
]

tasks

[
{
      "id": 1,
      "task": "Develop a responsive website for an e-commerce platform."
    },
    {
      "id": 2,
      "task": "Implement user authentication and authorization for a web application."
    },
    {
      "id": 3,
      "task": "Optimize database queries for improved performance."
    },
    {
      "id": 4,
      "task": "Design and develop a mobile app for tracking fitness goals."
    },
    {
      "id": 5,
      "task": "Deploy a scalable cloud infrastructure for a SaaS application."
    },
    {
      "id": 6,
      "task": "Implement a recommendation engine for a content-based news website."
    }
]
    
    ''']
  },
  {
    "role": "model",
    "parts": ['''
    1:3|2:2|3:2|4:3|5:1|6:4

  ]
}
    
    ''']
  },
]

  convo = model.start_chat(history=history)
  response = convo.send_message(json.dumps(data))  # Don't send unnecessary data
  print(response.text)

  return generate_distribution(response.text)