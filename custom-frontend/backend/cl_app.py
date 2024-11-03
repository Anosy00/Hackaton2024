# Chargement des modèles et des bibliothèques nécessaires
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import List
import torch
from typing import cast
from typing import Optional
import chainlit as cl
from dotenv import load_dotenv

# Importation de Hugging Face Transformers
from transformers import AutoModel, AutoTokenizer
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
import bs4

from langchain.document_loaders import PyMuPDFLoader as PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer

# Chargement des variables d'environnement
load_dotenv()

# Chargement des documents web et indexation avec embeddings
def initialize_vectorstore():
    # Liste des chemins des fichiers PDF
    pdf_files = [
        "pdf/R-1203-fr.pdf",  # Indiquez le chemin de votre fichier PDF
        "pdf/e_spirometrie_2017_VF.pdf",  # Ajoutez d'autres fichiers PDF ici
        "pdf/BreatheEasy-Diagnosis_optimized_FR.pdf"
    ]
    
    all_docs = []  # Pour stocker tous les documents chargés

    for file_path in pdf_files:
        loader = PDFLoader(file_path=file_path)
        docs = loader.load()
        all_docs.extend(docs)  # Ajouter les documents chargés à la liste

    # Diviser les documents en morceaux gérables
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    # Initialiser le modèle SentenceTransformer
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    class CustomEmbedding:
        def embed(self, texts: list[str]) -> list[list[float]]:
            return model.encode(texts, convert_to_numpy=True).tolist()

        def embed_documents(self, documents: list[str]) -> list[list[float]]:
            return self.embed(documents)

        def embed_query(self, query) -> list[float]:
            print(f"Requête à encoder : '{query}'")  # Débogage
            if isinstance(query, dict):
                query = query.get('question', '')
            if not query or not query.strip():
                raise ValueError("La requête est vide ou invalide.")
            return model.encode(query, convert_to_numpy=True).tolist()

    embedding_function = CustomEmbedding()

    # Extraire le texte et créer les embeddings
    texts = [doc.page_content for doc in splits if getattr(doc, 'page_content', '').strip()]
    if not texts:
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
    # Initialisation du modèle Bedrock avec configuration pour converser
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

    # Stockage de la chaîne RAG dans la session utilisateur
    cl.user_session.set("rag_chain", rag_chain)
    await cl.Message(content="Connected to Chainlit with RAG setup using Transformers Embeddings!").send()

@cl.on_message
async def on_message(message: cl.Message):
    if not message.content or not message.content.strip():  # Vérifie si le message n'est pas vide
        await cl.Message(content="La requête ne peut pas être vide.").send()
        return

    # Récupération de la chaîne RAG depuis la session utilisateur
    rag_chain = cast(Runnable, cl.user_session.get("rag_chain"))

    msg = cl.Message(content="")

    # Logique conditionnelle pour utiliser le retriever
    if "document" in message.content.lower():  # Condition simple pour déterminer si on utilise le retriever
        # Génération de la réponse en utilisant le flux asynchrone avec le retriever
        async for chunk in rag_chain.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)
    else:
        # Traitement alternatif si le retriever n'est pas utilisé
        response = "Je ne vais pas utiliser le retriever pour cette question. Réponse par défaut ou autre traitement."
        await msg.send(response)

    await msg.send()

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None
