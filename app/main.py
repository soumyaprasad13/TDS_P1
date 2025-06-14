from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

app = FastAPI()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

# Load data
with open("course.json") as f:
    course_data = json.load(f)

with open("discourse.json") as f:
    discourse_data = json.load(f)

# Flatten the text
course_chunks = [section["content"] for section in course_data if section.get("content")]
discourse_chunks = [post["content"] for post in discourse_data if post.get("content")]

all_chunks = course_chunks + discourse_chunks

# Embedder
model = SentenceTransformer("all-MiniLM-L6-v2")
chunk_embeddings = model.encode(all_chunks, convert_to_tensor=True)

class Question(BaseModel):
    question: str

@app.post("/api/")
async def answer_question(question: Question):
    try:
        q_embedding = model.encode(question.question, convert_to_tensor=True)
        similarities = cosine_similarity([q_embedding], chunk_embeddings)[0]
        top_k = 5
        top_indices = similarities.argsort()[-top_k:][::-1]
        retrieved_chunks = "\n".join([all_chunks[i] for i in top_indices])

        prompt = f"""You are a helpful TA for the TDS course.

Answer the following question using only the course content and discussion forum posts below.

Course content and posts:
{retrieved_chunks}

Question: {question.question}
Answer:"""

        response = client.chat.completions.create(
            model="openrouter/openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )

        return {"answer": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
