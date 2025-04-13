from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers # ou autre LLM local
from langchain.chains import RetrievalQA

# Charger le document
loader = TextLoader("data.txt")
documents = loader.load()
# Diviser le texte
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
# Créer les embeddings
embeddings = HuggingFaceEmbeddings()
db = FAISS.from_documents(texts, embeddings)
# Charger le LLM
llm = CTransformers(model="&lt;chemin vers votre modele&gt;", model_type="mistral")# exemple avec CTransformers et mistral
# Créer la chaîne de question-réponse
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=db.as_retriever())
# Poser une question
query = "Quelle est l'information principale dans le document ?"
print(qa.run(query))
