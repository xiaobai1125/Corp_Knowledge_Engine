# 🚀 Corp-Knowledge-Engine (企业智能知识库)

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/RAG-LangChain-green)](https://www.langchain.com/)

本项目整合了 **ETL 数据治理** 与 **RAG 智能问答** 两大核心模块，旨在解决企业数字化转型中的两大痛点：
1.  **数据杂**：多源异构数据（网页/PDF/Word）清洗困难，预训练语料质量低。
2.  **检索难**：通用大模型缺乏私有领域知识，且存在严重的“幻觉”问题。

## 📖 项目简介

这是一个基于 **RAG (检索增强生成)** 技术构建的企业级文档问答系统。

它可以将企业内部的非结构化文档（如 PDF 格式的法律法规、员工手册）转化为可检索的向量数据，并结合 **DeepSeek** 大模型提供精准的问答服务。本项目重点解决了大模型在私有领域知识上的**“幻觉”问题**。

> **注：** 本仓库为核心功能的开源脱敏版本，不包含敏感数据。

## ✨ 核心功能

1.  **数据清洗**：内置清洗脚本，自动去除 PDF 文档中的页眉、页脚、水印及乱码，保证入库数据质量。
2.  **精准检索**：集成 **BGE-Large-ZH** 中文向量模型，配合 ChromaDB 本地数据库，实现毫秒级、高准确度的语义检索。
3.  **溯源问答**：模型回答严格基于检索到的上下文，并且每一条回答都会标注**引用来源**，方便核查。
4.  **流式交互**：基于 Streamlit 开发的 Web 界面，支持打字机式的流式回复体验。

## 🛠️ 技术栈

- **语言**: Python 3.10
- **框架**: LangChain
- **向量库**: ChromaDB (本地持久化)
- **大模型**: DeepSeek-V3 (兼容 OpenAI 协议)
- **Embedding**: BAAI/bge-large-zh-v1.5
- **UI**: Streamlit

## 🚀 快速开始

### 1. 安装依赖

在终端执行

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

在项目的config.py中,填入你的key

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 3. 数据入库

将文件放入data/目录,运行:

```bash
python core_engine.py
```

### 📂 目录说明
```
├── config.py           # 全局配置文件
├── etl_pipeline.py     # [模块1] 数据采集与清洗脚本
├── core_engine.py      # [模块2] RAG 核心引擎
├── app.py              # [模块3] Streamlit 交互前端
├── api.py				# [模块4] API 接口
├── requirements.txt    # 项目依赖
└── data/               # 原始文档目录
```
*Created for Enterprise Knowledge Solutions.*
