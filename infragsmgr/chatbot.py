import openai
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# This class is used to interact with the OpenAI API
# and to generate responses based on the user's information
# fragments and questions.
class Chatbot:

  # initializes the chatbot with a specific model.
  def __init__(self, model="gpt-3.5-turbo"):
    self.model = model

  # This method is used to ask a question to the chatbot
  # based on the user's memories.
  def ask(self, question, memories):
    print("starting chatbot ask")
    print("question to chatbot: "+question)
    # concatenate the memories into a single string
    context = "\n".join(
      [f"- {m['text']} ({m['storage_date']})" for m in memories]
    )
    # prepare the prompt for the chatbot
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
    print("response from chatbot: "+question)
    return response

  # this method is used to ask a question to the chatbot
  # based on the user's information fragments.
  def queryInfrags(
    self,
    question,
    instructions,
    infrags
  ):
    print("starting chatbot queryInfrags")
    print("question to chatbot: "+question)
    # concatenate the information fragments into a single string
    context = "\n".join(
      [f"- {m['text']} ({m['storage_date']})" for m in infrags]
    )
    # prepare the prompt for the chatbot
    prompt = f"""
      {instructions}
      Voici les éléments d'information pertinents : {context}
      Voici la question : {question}
      Répond de manière claire, bienveillante, et uniquement
      en te basant sur les éléments d'information pertinents.

    """
    #  call the OpenAI API to get a response
    response = client.chat.completions.create(
      model=self.model,
      messages=[
        {"role": "system", "content": "Tu es un assistant mémoire personnel."},
        {"role": "user", "content": prompt}
      ],
      temperature=0.7
    )
    response = response.choices[0].message.content.strip()
    print("response from chatbot: "+response)
    return response

  # this method is generic to invoke chat gpt
  def askLLM(self, user_id, instructions, request):
    print("starting chatbot ask-llm")
    print("question to chatbot ask-llm: "+request)
    prompt = f"{instructions}\n{request}"
    response = client.chat.completions.create(
      model=self.model,
      messages=[
        {"role": "user", "content": prompt}
      ],
      temperature=0.7
    )
    response = response.choices[0].message.content.strip()
    print("response from chatbot ask-llm: "+response)
    return response
