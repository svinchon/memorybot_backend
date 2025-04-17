import openai
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Chatbot:

  def __init__(self, model="gpt-3.5-turbo"):
    self.model = model

  def ask(self, question, memories):
    print("question: "+question)
    context = "\n".join(
      [f"- {m['text']} ({m['date']})" for m in memories]
    )
    prompt = f"""
      Tu es un assistant personnel qui aide quelqu’un à se rappeler
      ses souvenirs.
      Voici les souvenirs pertinents : {context}
      Question : {question}
      Réponds de manière claire, bienveillante, et uniquement
      en te basant sur ces souvenirs.
    """
    response = client.chat.completions.create(
      model=self.model,
      messages=[
        {"role": "system", "content": "Tu es un assistant mémoire personnel."},
        {"role": "user", "content": prompt}
      ],
      temperature=0.7
    )
    response = response.choices[0].message.content.strip()
    print("response: "+question)
    return response
