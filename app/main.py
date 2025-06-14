from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
import os
import openai

# Load data
with open("data/course.json", "r", encoding="utf-8") as f:
    course_data = json.load(f)

with open("data/discourse.json", "r", encoding="utf-8") as f:
    discourse_data = json.load(f)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class Query(BaseModel):
    question: str
    image: Optional[str] = None

@app.post("/api/")
async def answer_question(query: Query):
    context_snippets = get_relevant_context(query.question)

    system_prompt = "You are a helpful Teaching Assistant for the Tools in Data Science course at IIT Madras. Answer based on the course and discussion forum content."

    full_prompt = system_prompt + "\n\nContext:\n" + context_snippets + f"\n\nQuestion: {query.question}\n\nAnswer:"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        answer_text = response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

    related_links = extract_links(context_snippets)

    return {
        "answer": answer_text.strip(),
        "links": related_links
    }

def get_relevant_context(question):
    matches = []
    keywords = question.lower().split()

    for topic in discourse_data:
        score = sum(kw in topic["title"].lower() for kw in keywords)
        if score > 0:
            posts = " ".join(topic["posts"])
            matches.append((score, topic["title"], posts, topic["url"]))

    for topic in course_data:
        text = topic.get("text", "") + " " + topic.get("title", "")
        score = sum(kw in text.lower() for kw in keywords)
        if score > 0:
            matches.append((score, topic["title"], text, ""))

    matches.sort(reverse=True)
    top_matches = matches[:3]

    context = ""
    for score, title, text, url in top_matches:
        context += f"\nTITLE: {title}\nCONTENT: {text[:1000]}\nLINK: {url}\n"

    return context

def extract_links(context):
    links = []
    for line in context.splitlines():
        if "https://" in line:
            links.append({
                "url": line.strip().replace("LINK: ", ""),
                "text": "Related link"
            })
    return links
