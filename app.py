import sys

# 注入 SQLite 补丁 (防止 Windows 报错)
try:
    import pysqlite3

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import streamlit as st
from config import Config
from core_engine import RagEngine

# 页面全局配置
st.set_page_config(
    page_title="企业级智能知识库",
    page_icon="🏢",
    layout="wide"
)


def main():
    # 1. 初始化引擎 (单例模式，防止刷新重载)
    if "engine" not in st.session_state:
        with st.spinner("系统初始化中... (正在加载 BGE 模型，请稍候)"):
            st.session_state.engine = RagEngine()
            try:
                st.session_state.engine.load_database()
            except:
                pass

                # 标题栏
    st.title("🏢 企业级智能知识库助手")
    st.caption(f"🚀 核心引擎：{Config.EMBEDDING_MODEL} (向量化) + {Config.LLM_MODEL} (大模型)")
    st.markdown("---")

    # 2. 侧边栏状态监控
    with st.sidebar:
        st.header("🖥️ 系统状态监控")

        # 数据库状态
        if st.session_state.engine.vector_store:
            st.success("🟢 向量数据库：已连接")
        else:
            st.error("🔴 向量数据库：未连接")
            st.warning("⚠️ 请先运行 `python core_engine.py` 进行数据入库！")

        st.divider()

        # 系统说明
        st.info(
            """
            **关于本系统：**
            本系统基于 RAG (检索增强生成) 架构。

            它能读取企业内部文档（如 PDF、Word），并结合大模型能力，提供**精准**、**有据可查**的问答服务。

            ✅ **杜绝幻觉**：仅基于文档回答
            ✅ **数据安全**：向量库本地部署
            """
        )

        st.markdown("---")
        st.markdown("© 2025 企业数字化研发部")

    # 3. 聊天界面初始化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "您好！我是您的智能业务助手。关于 ***(你想做的方向) 或公司规章制度，您有什么想问的吗？"}]

    # 渲染历史消息
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 处理用户输入
    if prompt := st.chat_input("请输入您的问题，例如：试用期最长可以签多久？"):
        # 显示用户问题
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在检索文档并思考中..."):
                try:
                    # 调用核心引擎
                    response = st.session_state.engine.query(prompt)
                    result = response["result"]
                    source_docs = response["source_documents"]

                    # 显示回答
                    st.write(result)

                    # 展示溯源 (Source Grounding)
                    with st.expander("📚 点击查看参考文档来源 (Source Grounding)"):
                        for idx, doc in enumerate(source_docs):
                            st.markdown(f"**来源片段 {idx + 1}:**")
                            st.info(f"...{doc.page_content[:200]}...")  # 展示前200个字

                    st.session_state.messages.append({"role": "assistant", "content": result})
                except Exception as e:
                    st.error(f"系统调用出错: {str(e)}")


if __name__ == "__main__":
    main()