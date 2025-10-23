import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()

# Configurez l'API Gemini avec votre clé.
# Assurez-vous que la variable d'environnement GOOGLE_API_KEY est définie.
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# This class is used to interact with the Gemini API
# and to generate responses based on the user's information
# fragments and questions.
class GoogleChatbot:

  #def __init__(self, model_name="gemini-1.5-flash"): # Modèle Gemini par défaut
  def __init__(self, model_name="gemini-2.0-flash"): # Modèle Gemini par défaut
    self.model = genai.GenerativeModel(model_name)
    self.llm = "Google"

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
    generation_config = genai.types.GenerationConfig(temperature=0.7)
    try:
      gemini_response = self.model.generate_content(
          [prompt], # Le prompt est passé comme une liste
          generation_config=generation_config,
          stream=True)
      gemini_response.resolve()
      response = gemini_response.text
    except Exception as e:
      print(f"Error calling Gemini API: {e}")
      response = "Désolé, une erreur est survenue lors de la génération de la réponse."
    print("response from chatbot: "+response)
    return response

  # this method is used to ask a question to the chatbot
  # based on the user's information fragments.
  def queryInfrags(
    self,
    question,
    instructions,
    infrags,
    language,
  ):
    print("starting chatbot queryInfrags")
    print("chatbot is: "+self.llm)
    print("language: "+language)
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
    generation_config = genai.types.GenerationConfig(temperature=0.7)
    try:
      gemini_response = self.model.generate_content(
          [prompt],
          generation_config=generation_config,
          stream=True)
      gemini_response.resolve()
      response = gemini_response.text
    except Exception as e:
      print(f"Error calling Gemini API: {e}")
      response = "Désolé, une erreur est survenue lors de la génération de la réponse."
    print("response from chatbot: "+response)
    return response

  # this method is generic to invoke chat gpt
  def askLLM(self, user_id, instructions, request, language):
    print("starting chatbot ask-llm")
    print("chatbot is: "+self.llm)
    print("language: "+language)
    print("question to chatbot ask-llm: "+request)
    prompt = f"{instructions}\n{request}"
    generation_config = genai.types.GenerationConfig(temperature=0.7)
    try:
      gemini_response = self.model.generate_content(
          [prompt],
          generation_config=generation_config,
          stream=True)
      gemini_response.resolve()
      response = gemini_response.text
    except Exception as e:
      print(f"Error calling Gemini API: {e}")
      response = "Désolé, une erreur est survenue lors de la génération de la réponse."
    print("response from chatbot ask-llm: "+response)
    return response
