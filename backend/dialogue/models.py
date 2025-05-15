from platform_functions.models import user_accounts, stock_transactions
from typing import List, Dict, Literal
from django.core.cache import cache
import requests

class Prompt():
    def __init__(self, role: Literal["system", "user", "assistant"] = "user", content: str = ""):
        self.role = role
        self.content = content

    def to_message(self):
        return {"role": self.role, "content": self.content}

class OllamaClient():
    def __init__(self, base_url: str, model_name: str, memorys: List[Prompt]):
        self.base_url = base_url if base_url else "http://localhost:11434/"
        self.model_name = model_name if model_name else "qwen3:4b"
        self.memorys = memorys if memorys else []
    
    def construct_message(self, prompts: List[Prompt]) -> List[Dict[str, str]]:
        message = []
        for memory in self.memorys:
            message.append(memory.to_message())
        for prompt in prompts:
            message.append(prompt.to_message())
            self.memorys.append(prompt)
        return message
    
    def chat(self, prompts: List[Prompt] | Prompt):
        if isinstance(prompts, Prompt):
            prompts = [prompts]
        
        request_url = self.base_url + "api/chat"
        message = self.construct_message(prompts)
        response = requests.post(
            request_url,
            json={
                "model": self.model_name,
                "messages": message,
                "stream": False
            }
        )

        response_content = response.json().get("message", {}).get("content", "")
        if "</think>" in response_content:
            thinking_content, content = response_content.replace("<think>", "").split("</think>", 1)
            thinking_content, content = thinking_content.replace("<think>", "").strip(), content.strip()
        else:
            content, thinking_content = response_content.strip(), None

        self.memorys.append(Prompt("assistant", content))
        return content, thinking_content
    
    def clear(self):
        self.memorys.clear()

'''
管理与模型对话的类，负责与视图层交互
拥有从数据库中加载上下文和初始化系统Prompt的功能
'''
class Agent():
    def __init__(self, user_id: int, **kwagrs):
        self.user_id = user_id
        self.memory_key = f"user_{self.user_id}_memory"
        self.client = None
        self.initialize(**kwagrs)
    
    def create(self):
        """ 初始化系统Prompt  """
        transactions = stock_transactions.objects.filter(
            user_id=user_accounts.objects.get(user_id=self.user_id)
        ).order_by("transaction_date")
        transaction_informations = [
            f"{transaction.transaction_date.strftime("%Y-%m-%d %H:%M")}"
            f"{"买入" if transaction.transaction_type==0 else "卖出"}了"
            f"{transaction.transaction_number}股{transaction.stock_name}，"
            f"每股价格为{transaction.per_price:.2f}，收益为{transaction.gains:.2f}"
            for transaction in transactions
        ]
        init_prompt = Prompt(
            role="system",
            content=f"""
            你是一个金融投资顾问，主攻领域是证券交易中的股票投资，你需要为用户提供投资的帮助和建议。
            此外你需要知道的是，这是一个集成多维股票分析的模拟证券交易平台，拥有多种功能，包含如下：
            1.股票基本信息查询、实时行情查询和历史行情查询；2.股票交易；3.股票技术指数（包含MACD、RSI、市盈率市销率等）；
            4.上市公司Z-score得分和简化夏普比率；5.使用Transformer预测下一个股票收盘价。
            在用户给你发送问题前，我会提供该用户的所有交易记录数据，包含交易类别、时间、股票名称、交易数量、每股价格和收益，信息如下：
            {transaction_informations}
            """
        )
        return [init_prompt]
    
    def load(self):
        """ 从缓存中加载对话记录  """
        user_memory = cache.get(self.memory_key)
        if not user_memory:
            return []
        if not isinstance(user_memory, List[Dict[str, str]]):
            raise ValueError("Memory is not a list of dict")
        memory = [Prompt(**prompt) for prompt in user_memory]
        return memory

    def initialize(self, **kwagrs):
        if not self.user_id:
            raise ValueError("User_id is not initialized")
        
        memory = self.load()
        if not memory:
            memory = self.create()

        self.client = OllamaClient(
            memorys=memory,
            base_url=kwagrs.get("base_url", None),
            model_name=kwagrs.get("model_name", None)
        )
    
    def send_message(self, user_content: str):
        return self.client.chat(Prompt("user", user_content))
    
    def close(self):
        messages = [
            prompt.to_message()
            for prompt in self.client.memorys
        ]
        cache.set(self.memory_key, messages)
        self.client.clear()
        del self.client