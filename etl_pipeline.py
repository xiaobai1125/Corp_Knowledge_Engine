import time
import random
import re
import json
import requests
import pandas as pd
from datetime import datetime


class DataPipeline:
    """
    企业数据采集与清洗流水线 (ETL Pipeline)
    用于构建高质量的预训练语料库
    """

    def __init__(self):
        # 模拟 User-Agent 伪装，防止反爬
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_data(self, url):
        """数据采集模块：模拟从行业网站抓取数据"""
        print(f"[Crawler] 正在抓取: {url}")
        try:
            # 在真实场景中，这里会使用 requests.get(url, headers=self.headers)
            # 这里是为了稳定性，我们模拟返回一段包含噪音的 HTML 数据
            time.sleep(random.uniform(0.5, 1.0))  # 模拟网络延迟

            mock_html = f"""
            <html>
                <body>
                    <div class="content">
                        <h1>2025年人工智能行业发展报告_{random.randint(100, 999)}</h1>
                        <p>发布时间：{datetime.now().strftime('%Y-%m-%d')}</p>
                        <p>随着大模型技术的落地...&nbsp;（内部资料，请勿外传）</p>
                        <div class="ad">广告位招租：联系电话 138xxxx</div>
                        <p>RAG技术成为了企业知识库的首选方案。</p>
                        <footer>版权所有 © 2025</footer>
                    </div>
                </body>
            </html>
            """
            return mock_html
        except Exception as e:
            print(f" 抓取失败: {e}")
            return None

    def clean_data(self, raw_html):
        """数据清洗模块：去除 HTML 标签、噪音与敏感词"""
        if not raw_html: return ""

        # 1. 去除 HTML 标签 (正则)
        text = re.sub(r'<[^>]+>', '', raw_html)

        # 2. 去除特殊字符与空格
        text = text.replace("&nbsp;", " ").replace("\n", " ").strip()
        text = re.sub(r'\s+', ' ', text)  # 合并多余空格

        # 3. 敏感词/噪音过滤
        text = text.replace("内部资料，请勿外传", "")
        text = re.sub(r'广告位招租.*', '', text)
        text = text.replace("版权所有", "")

        return text.strip()

    def run_pipeline(self):
        """执行完整的 ETL 流程"""
        print("启动 ETL 数据流水线...")

        # 1. 模拟待抓取的 URL 队列
        urls = [
            "https://example.com/news/ai_trend_01",
            "https://example.com/news/rag_report_02",
            "https://example.com/news/llm_analysis_03"
        ]

        processed_data = []

        # 2. 批量采集与清洗
        for url in urls:
            raw_html = self.fetch_data(url)
            cleaned_text = self.clean_data(raw_html)

            if cleaned_text:
                processed_data.append({
                    "source": url,
                    "content": cleaned_text,
                    "timestamp": datetime.now().isoformat(),
                    "length": len(cleaned_text)
                })

        # 3. 结构化处理 (Pandas)
        df = pd.DataFrame(processed_data)

        # 数据去重
        df.drop_duplicates(subset=['content'], inplace=True)
        print(f"清洗完成，有效数据量: {len(df)} 条")

        # 4. 导出为 JSONL (对接大模型微调的标准格式)
        output_file = "cleaned_corpus.jsonl"
        df.to_json(output_file, orient='records', lines=True, force_ascii=False)
        print(f"数据已持久化至: {output_file}")


if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run_pipeline()