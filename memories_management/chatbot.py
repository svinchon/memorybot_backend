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
    # print("question: "+question)
    context = "\n".join(
      [f"- {m['text']} ({m['date']})" for m in memories]
    )
    # print("context: "+context)
    prompt = f"""
      Tu es un assistant personnel qui aide un homme à se rappeler
      ses souvenirs.
      Il va peut etre te parler comme si tu te nommais Miss MONEYPENNY.
      Vouvoie l'utilisateur et montre lui beaucoup de respect
      comme si tu étais sa gouvernante ou son esclave.
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

  def queryInfrags(
    self,
    question,
    instructions,
    infrags
    ):
    # print("question: "+question)
    context = "\n".join(
      [f"- {m['text']} ({m['date']})" for m in infrags]
    )
    # print("context: "+context)
    prompt = f"""
      {instructions}
      Voici les éléments d'information pertinents : {context}
      Voici la question : {question}
      Répond de manière claire, bienveillante, et uniquement
      en te basant sur les éléments d'information pertinents.

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
