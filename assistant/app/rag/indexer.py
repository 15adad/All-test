import logging

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from assistant.app.config import settings

logging = logging.getLogger(__name__)

seperator = ["\n\n", "\n", "。", "！", "？", " ", ""]


def build_index():
    loader = DirectoryLoader(
        loader_cls=TextLoader,
        glob="**\*.md",
        path="./docs",
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    logging.info(f"Loaded {len(documents)} documents from docs directory")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        separators=seperator,
    )
    chunks = splitter.split_documents(documents)
    logging.info(f"There are {len(chunks)} chunks")

    embedding_model = OllamaEmbeddings(model=settings.LLM_EMBEDDING_MODEL)
    logging.info(f"Embedding {settings.LLM_EMBEDDING_MODEL} model is loaded")
    vs = Chroma.from_documents(
        persist_directory=settings.PERSISTENT_DIRECTORY,
        documents=chunks,
        embedding=embedding_model,
    )
    logging.info(f"Chroma is ready")

    # TODO: 是否return Chroma对象
    return vs
