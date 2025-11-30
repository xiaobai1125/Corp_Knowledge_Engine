import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# 导入我们写的核心逻辑
from core_engine import RagEngine


# --- 定义数据模型 ---
class QueryRequest(BaseModel):
    question: str  # 用户传来的问题


class QueryResponse(BaseModel):
    answer: str  # AI 回答
    sources: list  # 参考来源


# --- 全局引擎实例 ---
engine = None


# --- 生命周期管理 (启动时加载模型) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    print("正在启动 API 服务，加载 AI 引擎...")
    try:
        engine = RagEngine()
        engine.load_database()  # 加载向量库
        print("引擎加载完成！")
    except Exception as e:
        print(f"引擎加载失败: {e}")
    yield
    print("服务关闭")


# --- 初始化 App ---
app = FastAPI(
    title="Corp-Knowledge-Engine API",
    version="1.0",
    description="企业级 RAG 智能问答接口服务",
    lifespan=lifespan
)


# --- 接口定义 ---
@app.get("/")
def health_check():
    """健康检查接口"""
    return {"status": "online", "model": "DeepSeek + BGE"}


@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    """
    核心问答接口
    输入: {"question": "..."}
    输出: {"answer": "...", "sources": [...]}
    """
    global engine
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        # 调用核心逻辑 (和你 Streamlit 里调用的是同一个！)
        result = engine.query(request.question)

        # 整理返回格式
        response = {
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 启动服务：localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)