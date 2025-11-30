import os
import re
import logging
from typing import List

# 导入 LangChain 组件
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# 导入配置
from config import Config

# 配置企业级日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [Engine] %(message)s')
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    ETL Pipeline: 负责数据的加载、清洗与切片
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """工业级清洗逻辑：去除页眉页脚、乱码与水印噪音"""
        if not text: return ""
        # 去除空字节
        text = re.sub(r'\x00', '', text)
        # 去除类似 "Page 1 of 10" 的页码
        text = re.sub(r'Page \d+ of \d+', '', text)
        # 去除 "仅供内部参考" 等水印 (模拟)
        text = text.replace("仅供内部参考", "").replace("Confidential", "")
        # 修复断行 (将被意外切断的句子连起来)
        text = re.sub(r'\n+', '\n', text).strip()
        return text

    def ingest_pdf(self, file_path: str) -> List:
        """处理单个 PDF 文件"""
        logger.info(f"Starting ingestion task: {file_path}")
        try:
            # 1. Load
            loader = PyPDFLoader(file_path)
            raw_docs = loader.load()

            # 2. Clean
            for doc in raw_docs:
                doc.page_content = self.clean_text(doc.page_content)

            # 3. Split
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP
            )
            splits = splitter.split_documents(raw_docs)
            logger.info(f"Document processed. Generated {len(splits)} chunks.")
            return splits
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise


class RagEngine:
    """
    RAG Engine: 负责向量库管理与问答链路
    """

    def __init__(self):
        # 初始化 Embedding 模型 (第一次运行会下载 BGE 模型，约 1.2GB)
        logger.info(f"Loading Embedding Model: {Config.EMBEDDING_MODEL} ...")
        self.embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        self.vector_store = None
        self.qa_chain = None

    def build_database(self, documents: List):
        """构建并持久化向量数据库"""
        if not documents:
            logger.warning("No documents to ingest.")
            return

        logger.info(f"Persisting {len(documents)} vectors to {Config.VECTOR_DB_DIR}...")
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=Config.VECTOR_DB_DIR
        )
        logger.info("Database successfully built.")

    def load_database(self):
        """加载已存在的数据库"""
        if os.path.exists(Config.VECTOR_DB_DIR):
            self.vector_store = Chroma(
                persist_directory=Config.VECTOR_DB_DIR,
                embedding_function=self.embeddings
            )
            logger.info("Vector database loaded from disk.")
        else:
            logger.error("Database not found. Please run data ingestion first.")

    def init_llm(self):
        """初始化大模型与问答链"""
        if not self.vector_store:
            self.load_database()

        logger.info(f"Connecting to LLM: {Config.LLM_MODEL}...")
        llm = ChatOpenAI(
            model_name=Config.LLM_MODEL,
            api_key=Config.API_KEY,
            base_url=Config.LLM_API_BASE,
            temperature=0.1  # 低温度保证严谨性
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": Config.RETRIEVAL_K}),
            return_source_documents=True
        )
        logger.info("RAG Chain initialized.")

    def query(self, question: str):
        """对外暴露的问答接口"""
        if not self.qa_chain:
            self.init_llm()
        return self.qa_chain.invoke({"query": question})


# --- ETL 入口 (命令行运行) ---
if __name__ == "__main__":
    # 1. 准备环境
    processor = DataProcessor()
    engine = RagEngine()

    # 2. 检查数据目录
    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
        logger.warning(f"Created data folder: {Config.DATA_DIR}. Please put your PDF files here!")
    else:
        # 3. 遍历并处理所有 PDF
        all_splits = []
        for filename in os.listdir(Config.DATA_DIR):
            if filename.endswith(".pdf"):
                file_path = os.path.join(Config.DATA_DIR, filename)
                splits = processor.ingest_pdf(file_path)
                all_splits.extend(splits)

        # 4. 存入数据库
        if all_splits:
            engine.build_database(all_splits)
        else:
            logger.warning("No PDF files found in ./data directory.")