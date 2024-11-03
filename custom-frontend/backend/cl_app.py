# Importation des bibliothèques et modules nécessaires
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import List, Optional, cast
import chainlit as cl
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import pipeline  # Pour l'analyse de sentiment
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4
import textstat  # Pour l'évaluation du niveau de lisibilité
from langchain.document_loaders import PyMuPDFLoader as PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
import urllib

# Chargement des variables d'environnement
load_dotenv()

# Chargement des modèles pour l'analyse de sentiment
sentiment_model_name = "distilbert-base-uncased-finetuned-sst-2-english"
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)

# Chargement des documents PDF et indexation avec embeddings
def initialize_vectorstore():
    pdf_files = [
        "pdf/R-1203-fr.pdf",
        "pdf/e_spirometrie_2017_VF.pdf",
        "pdf/BreatheEasy-Diagnosis_optimized_FR.pdf"
    ]
    
    all_docs = []
    for file_path in pdf_files:
        loader = PDFLoader(file_path=file_path)
        docs = loader.load()
        all_docs.extend(docs)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    class CustomEmbedding:
        def embed(self, texts: list[str]) -> list[list[float]]:
            return model.encode(texts, convert_to_numpy=True).tolist()

        def embed_documents(self, documents: list[str]) -> list[list[float]]:
            return self.embed(documents)

        def embed_query(self, query) -> list[float]:
            if isinstance(query, dict):
                query = query.get('question', '')
            if not query or not query.strip():
                raise ValueError("La requête est vide ou invalide.")
            return model.encode(query, convert_to_numpy=True).tolist()

    embedding_function = CustomEmbedding()

    texts = [doc.page_content for doc in splits if getattr(doc, 'page_content', '').strip()]
    if not texts:
        raise ValueError("Aucun texte valide à indexer dans le vectorstore.")

    embeddings = embedding_function.embed(texts)

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function
    )
    return vectorstore

vectorstore = initialize_vectorstore()
retriever = vectorstore.as_retriever()

# Fonction pour formater les documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Détermine le niveau de complexité du langage de l'utilisateur
def determine_user_level(text: str) -> str:
    readability_score = textstat.flesch_reading_ease(text)
    if readability_score < 50:
        return "expert"
    elif readability_score < 70:
        return "intermediate"
    else:
        return "novice"

# Génère un prompt adapté au niveau de l'utilisateur
def get_custom_prompt(level: str) -> ChatPromptTemplate:
    if level == "expert":
        return ChatPromptTemplate.from_messages(
            [
                ("system", "Vous êtes un assistant médical spécialisé."),
                ("human", "{context}\n\n{question}"),
            ]
        )
    elif level == "intermediate":
        return ChatPromptTemplate.from_messages(
            [
                ("system", "Vous êtes un assistant bien informé en santé."),
                ("human", "Expliquez en termes clairs et concis :\n\n{context}\n\n{question}"),
            ]
        )
    else:
        return ChatPromptTemplate.from_messages(
            [
                ("system", "Vous êtes un assistant accessible et éducatif."),
                ("human", "Expliquez simplement pour un public général :\n\n{context}\n\n{question}"),
            ]
        )

# Fonction pour analyser le sentiment d'un message
def analyze_sentiment(message: str) -> str:
    result = sentiment_analyzer(message)[0]
    sentiment = result['label']
    score = result['score']
    return f"{sentiment} ({score:.2f})"

# Fonction de démarrage du chat
@cl.on_chat_start
async def on_chat_start():
    llm = ChatBedrockConverse(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-west-2",
        temperature=0,
        max_tokens=None
    )

    # Prompt de démarrage par défaut
    default_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant.",
            ),
            ("human", "{context}\n\n{question}"),
        ]
    )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | default_prompt
        | llm
        | StrOutputParser()
    )

    cl.user_session.set("rag_chain", rag_chain)
    await cl.Message(content="Salut ! Comment je peux t'aider aujourd'hui ?").send()

# Fonction pour gérer les messages entrants
@cl.on_message
async def on_message(message: cl.Message):
    # Détection "rick roll"
    if message.content.lower() == "rick roll":
        elements = [cl.Video(name="rickroll.mp4", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", display="inline")]
        await cl.Message(content="RICK ROLLED", elements=elements).send()
        return

    # Analyse du sentiment de l'utilisateur
    sentiment_result = analyze_sentiment(message.content)
    
    # Analyse du niveau lexical de l'utilisateur et création d'un prompt personnalisé
    user_level = determine_user_level(message.content)
    custom_prompt = get_custom_prompt(user_level)
    
    # Créer la chaîne RAG avec le prompt personnalisé
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_prompt
        | ChatBedrockConverse(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name="us-west-2",
            temperature=0,
            max_tokens=None
        )
        | StrOutputParser()
    )

    keywords = ["spirométrie", "diagnostic", "respiration", "santé", "asthme"]
    if any(keyword in message.content.lower() for keyword in keywords):
        retrieved_docs = retriever.get_relevant_documents(message.content)
        if retrieved_docs:
            context = format_docs(retrieved_docs)
            input_data = {"context": context, "question": message.content}
            msg = cl.Message(content="")  # Message prêt pour le streaming
            async for chunk in rag_chain.astream(input_data, config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()])):
                await msg.stream_token(chunk)
            await msg.send()  # Envoie une fois la réponse complète
        else:
            await cl.Message(content="Aucun document pertinent trouvé. Réponse basée sur le modèle...").send()
    else:
        response = rag_chain.astream(
            {"question": f"Répondez à cette question en fonction du niveau '{user_level}': {message.content}"},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        )
        msg = cl.Message(content="")  # Message pour le streaming
        async for chunk in response:
            await msg.stream_token(chunk)

    # Envoyer une réponse concernant le sentiment analysé
    await cl.Message(content=f"Analyse du sentiment : {sentiment_result}").send()
