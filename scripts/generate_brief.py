#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 新闻简报生成器
使用 DeepSeek/OpenAI API 分析新闻并生成个性化简报
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from {env_path}")
else:
    print("No .env file found, using environment variables")

import requests


class AIBriefGenerator:
    # Provider configurations with priority order (fallback chain)
    PROVIDER_CONFIGS = [
        {
            'name': 'github_models',
            'api_key_env': 'GITHUB_TOKEN',
            'base_url': 'https://models.inference.ai.azure.com',
            'model': 'gpt-4o-mini',
            'headers': lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        },
        {
            'name': 'openrouter',
            'api_key_env': 'OPENROUTER_API_KEY',
            'base_url': 'https://openrouter.ai/api/v1',
            'model': 'google/gemini-flash-1.5',
            'headers': lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com",
                "X-Title": "Daily News Brief"
            }
        },
        {
            'name': 'deepseek',
            'api_key_env': 'DEEPSEEK_API_KEY',
            'base_url_env': 'DEEPSEEK_BASE_URL',
            'base_url_default': 'https://api.deepseek.com/v1',
            'model_env': 'DEEPSEEK_MODEL',
            'model_default': 'deepseek-chat',
            'headers': lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        },
        {
            'name': 'moonshot',
            'api_key_env': 'MOONSHOT_API_KEY',
            'base_url_env': 'MOONSHOT_BASE_URL',
            'base_url_default': 'https://api.moonshot.cn/v1',
            'model_env': 'MOONSHOT_MODEL',
            'model_default': 'moonshot-v1-8k',
            'headers': lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        },
        {
            'name': 'qwen',
            'api_key_env': 'QWEN_API_KEY',
            'base_url_env': 'QWEN_BASE_URL',
            'base_url_default': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'model_env': 'QWEN_MODEL',
            'model_default': 'qwen-turbo',
            'headers': lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        },
    ]

    def __init__(self):
        self.data_dir = project_root / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        # Try providers in order until one works
        self.provider = None
        self.api_key = None
        self.base_url = None
        self.model = None
        self.headers_func = None
        
        # Get preferred provider from env, if any
        preferred_provider = os.getenv('DEFAULT_AI_PROVIDER', '').lower()
        
        # Reorder configs to put preferred provider first
        configs = self.PROVIDER_CONFIGS.copy()
        if preferred_provider:
            for i, config in enumerate(configs):
                if config['name'] == preferred_provider:
                    configs.insert(0, configs.pop(i))
                    break
        
        # Try each provider
        for config in configs:
            if self._try_init_provider(config):
                break
        
        if not self.provider:
            raise ValueError("No available AI provider found. Please set at least one API key.")
        
        print(f"Using AI provider: {self.provider}, model: {self.model}")

    def _try_init_provider(self, config):
        """Try to initialize a provider, return True if successful"""
        api_key = os.getenv(config['api_key_env'])
        if not api_key:
            return False
        
        # Check for payment/balance errors by making a test request
        # Handle both direct base_url and env-based configuration
        if 'base_url_env' in config:
            base_url = os.getenv(config['base_url_env'], config.get('base_url_default', ''))
        else:
            base_url = config['base_url']
        
        if 'model_env' in config:
            model = os.getenv(config['model_env'], config.get('model_default', ''))
        else:
            model = config['model']
        
        headers = config['headers'](api_key)
        
        # Test the provider with a minimal request
        try:
            test_payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            }
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self.provider = config['name']
                self.api_key = api_key
                self.base_url = base_url
                self.model = model
                self.headers_func = config['headers']
                return True
            elif response.status_code in [402, 429]:
                print(f"Provider {config['name']} has insufficient balance or quota, skipping...")
                return False
            else:
                print(f"Provider {config['name']} returned status {response.status_code}, skipping...")
                return False
                
        except Exception as e:
            print(f"Provider {config['name']} test failed: {e}, skipping...")
            return False

    def load_news_data(self):
        """加载新闻数据"""
        news_file = self.data_dir / 'news.json'
        if not news_file.exists():
            raise FileNotFoundError("news.json not found. Please run fetch_news.py first.")

        with open(news_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def prepare_news_context(self, news_data, max_items=50):
        """准备新闻上下文，选择热度最高的新闻"""
        news_list = news_data.get('news', [])
        # 按热度排序
        sorted_news = sorted(news_list, key=lambda x: x.get('hotness', 0), reverse=True)
        selected_news = sorted_news[:max_items]

        context = []
        for i, news in enumerate(selected_news, 1):
            context.append(f"{i}. [{news.get('source', '未知来源')}] {news.get('title', '')}")

        return "\n".join(context)

    def call_ai_api(self, prompt):
        """调用AI API"""
        headers = self.headers_func(self.api_key)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的新闻分析师，擅长为科研学者提供有价值的新闻洞察。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error calling AI API: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text if hasattr(e.response, 'text') else e.response}")
            raise

    def generate_brief(self):
        """生成新闻简报"""
        print("Loading news data...")
        news_data = self.load_news_data()
        news_context = self.prepare_news_context(news_data)

        # 构建Prompt
        prompt = f"""你是一位资深新闻分析师和职业规划顾问。请根据以下今日热点新闻，为一位40岁左右的基础科研学者进行深度分析，生成个性化新闻简报。

用户画像：
- 年龄：40岁左右
- 职业：基础科研学者（普通科研人员，可能是副教授/副研究员级别）
- 目标：1) 做好科研，争取职称晋升 2) 了解世界大事，拓展视野 3) 寻找挣钱/投资机会，改善经济状况（如基金投资、副业等）
- 痛点：科研压力大、收入有限、时间紧张、需要平衡学术与家庭
- 关注点：科研 funding 机会、学术趋势、经济金融、投资机会、国际局势、知识变现

今日新闻列表：
{news_context}

请从以下四个维度进行深度分析，并严格按照JSON格式输出：

{{
    "section1": {{
        "headline": "头条新闻标题",
        "headline_analysis": "深度分析：这条新闻的核心价值、深层原因、对科研学者的特殊意义（3-4句话，要有洞察力）",
        "top_news": [
            {{"title": "新闻标题1", "source": "来源", "relevance": "深度解读：这条新闻与科研/投资/时事的内在关联，为什么值得关注"}},
            {{"title": "新闻标题2", "source": "来源", "relevance": "深度解读：这条新闻与科研/投资/时事的内在关联，为什么值得关注"}},
            {{"title": "新闻标题3", "source": "来源", "relevance": "深度解读：这条新闻与科研/投资/时事的内在关联，为什么值得关注"}}
        ],
        "trend_insight": "深度趋势洞察：基于今日新闻提炼出的宏观趋势、潜在机会或风险预警（3-4句话，要有前瞻性）"
    }},
    "section2": {{
        "research_funding": "科研 funding 深度分析：1) 今日新闻中隐含的 funding 机会 2) 政策导向分析 3) 具体建议如何申请或对接（4-5句话， actionable）",
        "academic_opportunities": "学术机会深度分析：1) 今日新闻反映的学术趋势 2) 可能的合作机会 3) 对职业发展的启示（4-5句话）",
        "international_trends": "国际趋势深度分析：1) 国际局势对科研的影响 2) 国际合作机会 3) 需要关注的风险（4-5句话）",
        "investment_insights": "投资理财深度分析：1) 基于今日新闻的市场判断 2) 具体投资建议（基金/股票/其他）3) 风险提示 4) 适合科研学者的理财策略（5-6句话，具体可操作）"
    }},
    "section3": {{
        "learning_tracks": [
            {{"title": "学习主题1", "description": "为什么学：学习价值分析；学什么：核心内容；怎么用：应用到科研或投资的具体路径（详细具体）"}},
            {{"title": "学习主题2", "description": "为什么学：学习价值分析；学什么：核心内容；怎么用：应用到科研或投资的具体路径（详细具体）"}},
            {{"title": "学习主题3", "description": "为什么学：学习价值分析；学什么：核心内容；怎么用：应用到科研或投资的具体路径（详细具体）"}}
        ],
        "action_advice": "本周行动清单：1) 科研方面具体做什么 2) 投资方面具体做什么 3) 学习方面具体做什么 4) 其他重要行动（分点列出，具体可执行）"
    }},
    "section4": {{
        "term": "核心知识点名称（基于新闻热点选择最有价值的概念）",
        "definition": "精准定义：用专业但易懂的语言解释这个概念的本质（2-3句话）",
        "origin": "深度溯源：1) 概念起源 2) 发展历程 3) 关键人物或事件（3-4句话）",
        "importance": "价值分析：1) 为什么对40岁科研学者重要 2) 如何影响科研/投资/生活 3) 掌握后的收益（4-5句话）",
        "trends": "趋势预判：1) 当前发展态势 2) 未来3-5年发展方向 3) 科研学者如何提前布局（4-5句话，有前瞻性）"
    }}
}}

深度分析要求：
1. 避免泛泛而谈，每个分析都要有具体依据和 actionable insights
2. 投资建议要具体到基金类型、行业板块或策略，不要只说"关注市场"
3. 知识扩展要深入：定义精准、由来有历史感、重要性结合用户画像、趋势有预判性
4. 语言风格：专业、睿智、有洞察力，像一位经验丰富的导师
5. 站在40岁科研学者的角度思考：时间有限、需要平衡、追求稳健增长
"""

        print(f"Calling {self.provider} API to generate brief...")
        ai_response = self.call_ai_api(prompt)

        # 解析JSON响应
        try:
            # 清理可能的markdown代码块
            cleaned_response = ai_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]

            brief_data = json.loads(cleaned_response.strip())
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            print(f"AI Response:\n{ai_response}")
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                brief_data = json.loads(json_match.group())
            else:
                raise

        # 添加元数据
        brief_data['meta'] = {
            'generated_at': datetime.now().isoformat(),
            'ai_provider': self.provider,
            'model': self.model,
            'news_count': len(news_data.get('news', [])),
            'update_time': news_data.get('update_time', '')
        }

        return brief_data

    def save_brief(self, brief_data):
        """保存简报到文件"""
        brief_file = self.data_dir / 'brief.json'
        with open(brief_file, 'w', encoding='utf-8') as f:
            json.dump(brief_data, f, ensure_ascii=False, indent=2)
        print(f"Brief saved to {brief_file}")

    def run(self):
        """运行简报生成"""
        print("=" * 60)
        print("AI News Brief Generator")
        print("=" * 60)

        try:
            brief_data = self.generate_brief()
            self.save_brief(brief_data)
            print("\nBrief generated successfully!")
            return True
        except Exception as e:
            print(f"\nError generating brief: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    generator = AIBriefGenerator()
    success = generator.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
