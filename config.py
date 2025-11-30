import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    # 基础配置
    APP_NAME = "Corp-Knowledge-Engine"
    VERSION = "1.2.0"

    # 模型配置
    EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"
    LLM_MODEL = "deepseek-chat"
    LLM_API_BASE = "https://api.deepseek.com"
    API_KEY = "***************" # 填入你的API Key从环境变量读取，安全！

    # 路径配置
    DATA_DIR = "./data"
    VECTOR_DB_DIR = "./chroma_db"

    # RAG参数
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    RETRIEVAL_K = 3