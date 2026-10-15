import logging

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredFileLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PERSIST_DIR = "./chroma_db"
logger = logging.getLogger(__file__)
# 自定义分隔符按优先级排序依次为段落、行、句号、感叹号、问号、空格、空字符串来切分
separators = ["\n\n", "\n", "。", "！", "？", " ", ""],


def build_vectorstore():
    # 1.Loader 文档知识库,加载 docs 目录下所有 txt，DirectoryLoader 只管遍历目录、找出文件
    loader = DirectoryLoader(
        "docs",
        glob="**/*.txt",  # 递归加载docs下所有的txt文件
        loader_cls=UnstructuredFileLoader,  # 真正加载的loader类，自动识别文件类型，支持txt、pdf、docx等
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents from docs directory")
    # 2.切块chunk,递归字符切分
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=20,  # 每个chunk的最大字符数
        chunk_overlap=5,  # 每个chunk之间的重叠字符数
        separators=separators,
    )

    chunks = splitter.split_documents(documents)
    logger.info(f"{len(chunks)} chunks are created")
    # 3.向量化chunk,embedding嵌入
    embedding_model = OllamaEmbeddings(model="bge-m3")
    logger.info(f"Embedding model is loaded")
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=PERSIST_DIR,
    )
    logger.info(f"Chroma is ready")

# 从磁盘里加载向量数据库，用于后续的查询和检索
def _load_vectorstore():
    embedding_model = OllamaEmbeddings(model="bge-m3")
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embedding_model,
    )