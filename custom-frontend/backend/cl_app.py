# Chargement des modèles et des bibliothèques nécessaires
import os
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import List
import torch
from typing import cast
import chainlit as cl
from dotenv import load_dotenv

# Importation de Hugging Face Transformers
from transformers import AutoModel, AutoTokenizer
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4

from langchain.document_loaders import PyMuPDFLoader as PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer

# Chargement des variables d'environnement
load_dotenv()

# Définir la taille maximale des fichiers (30 Mo)
MAX_TOTAL_SIZE = 30 * 1024 * 1024  # 30 Mo en octets

    # Diviser les documents en morceaux gérables
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Initialiser le modèle SentenceTransformer
    model_name = "all-MiniLM-L6-v2"  # Exemple de modèle Sentence Transformer
    model = SentenceTransformer(model_name)

    class CustomEmbedding:
        def embed(self, texts: list[str]) -> list[list[float]]:
            return model.encode(texts, convert_to_numpy=True).tolist()

        def embed_documents(self, documents: list[str]) -> list[list[float]]:
            return self.embed(documents)

        def embed_query(self, query) -> list[float]:
            print(f"Requête à encoder : '{query}'")  # Débogage
            if isinstance(query, dict):
                query = query.get('question', '')  # Récupère la question du dict
            if not query or not query.strip():  # Vérifie si la requête est vide
                raise ValueError("La requête est vide ou invalide.")  # Gestion d'erreur
            return model.encode(query, convert_to_numpy=True).tolist()

    embedding_function = CustomEmbedding()

    # Extraire le texte et créer les embeddings
    texts = [doc.page_content for doc in splits if getattr(doc, 'page_content', '').strip()]  # Filtrer les documents vides
    if not texts:  # Vérifie si nous avons des textes valides
        raise ValueError("Aucun texte valide à indexer dans le vectorstore.")

    embeddings = embedding_function.embed(texts)

    # Créer le vectorstore avec les embeddings et les textes
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function
    )
    return vectorstore


vectorstore = initialize_vectorstore()
retriever = vectorstore.as_retriever()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@cl.on_chat_start
async def on_chat_start():
    """Initialise la conversation avec le modèle LLM."""
    llm = ChatBedrockConverse(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-west-2",
        temperature=0,
        max_tokens=None
    )

    # Prompt pour générer des réponses en utilisant les documents pertinents
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant.",
            ),
            ("human", "{context}\n\n{question}"),
        ]
    )

    # Création de la chaîne RAG
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    files = None

    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a text file to begin!", accept=["text/plain"]
        ).send()
    # Stockage de la chaîne RAG dans la session utilisateur
    cl.user_session.set("rag_chain", rag_chain)
    await cl.Message(content="Connected to Chainlit with RAG setup using Transformers Embeddings!").send()

    text_file = files[0]

    with open(text_file.path, "r", encoding="utf-8") as f:
        text = f.read()

    # Let the user know that the system is ready
    await cl.Message(
        content=f"`{text_file.name}` uploaded, it contains {len(text)} characters!"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    if not message.content or not message.content.strip():  # Vérifie si le message n'est pas vide
        await cl.Message(content="La requête ne peut pas être vide.").send()
        return
    """Gère les messages reçus de l'utilisateur."""
    runnable = cast(Runnable, cl.user_session.get("runnable"))

    # Récupération de la chaîne RAG depuis la session utilisateur
    rag_chain = cast(Runnable, cl.user_session.get("rag_chain"))

    msg = cl.Message(content="")
    
    # Génération de la réponse en utilisant le flux asynchrone
    async for chunk in rag_chain.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()



@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Gère l'authentification par mot de passe."""
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

def process_file(filepath):
    """Détermine le type de fichier et le traite en conséquence."""
    file_extension = os.path.splitext(filepath)[1].lower()

    if file_extension in ['.txt', '.pdf', '.docx', '.csv']:
        return handle_document(filepath)
    elif file_extension in ['.png', '.jpg', '.jpeg', '.gif']:
        return handle_image(filepath)
    elif file_extension in ['.mp3', '.wav', '.ogg']:
        return handle_audio(filepath)
    else:
        return "Type de fichier non supporté."

def handle_document(filepath):
    """Logique pour traiter les documents."""
    with open(filepath, 'r') as f:
        content = f.read()
    return f"Document traité avec succès. Contenu extrait : {content[:100]}..."  # Retourner les 100 premiers caractères

def handle_image(filepath):
    """Logique pour traiter les images."""
    return f"Image {os.path.basename(filepath)} traitée avec succès."

def handle_audio(filepath):
    """Logique pour traiter les fichiers audio."""
    return f"Fichier audio {os.path.basename(filepath)} traité avec succès."
