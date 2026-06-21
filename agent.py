import requests
import json
import re
from tools.web_search import web_search
from tools.translator import translate
from tools.weather import get_weather

# ============================================================
# 工具注册表
# ============================================================
TOOLS = {
    "web_search": {
        "func": web_search,
        "desc": "用Bing搜索互联网获取最新信息。输入：搜索关键词"
    },
    "translate": {
        "func": translate,
        "desc": "将英文翻译成中文。输入：英文文本"
    },
    "get_weather": {
        "func": get_weather,
        "desc": "获取城市天气预报。输入：城市名（中文或英文，如：北京、Shanghai）"
    }
}

QWEN_URL = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "/data/Newdisk/xugan/models/Qwen3-8B"

def call_qwen(messages: list) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.6,
    }
    resp = requests.post(QWEN_URL, json=payload, timeout=60)
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    return content

def parse_action(text: str):
    action, action_input = None, None
    for line in text.strip().split("\n"):
        if line.startswith("Action:"):
            action = line.replace("Action:", "").strip()
        if line.startswith("Action Input:"):
            action_input = line.replace("Action Input:", "").strip()
    return action, action_input

def run_agent(user_question: str, max_steps: int = 5) -> str:
    print(f"\n{'='*50}")
    print(f"用户问题: {user_question}")
    print(f"{'='*50}")

    tools_desc = "\n".join([f"- {name}: {info['desc']}" for name, info in TOOLS.items()])

    system_prompt = f"""你是一个智能助手，可以使用工具来回答问题。

可用工具：
{tools_desc}

你必须严格按照以下格式一步一步回答，每次只输出一个步骤：

Thought: 我的思考过程
Action: 工具名称（只能是 web_search、translate 或 get_weather）
Action Input: 传给工具的内容

当你获得足够信息后，用以下格式给出最终答案：
Thought: 我已经有足够的信息了
Final Answer: 这里写最终的中文答案

规则：
1. 每次只输出一个 Action
2. 问天气相关问题用 get_weather
3. 问知识性问题用 web_search
4. 遇到英文内容需要翻译时用 translate
5. 最终答案必须是中文
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    for step in range(1, max_steps + 1):
        print(f"\n--- 第 {step} 步 ---")
        response = call_qwen(messages)
        print(f"Qwen 回复:\n{response}")

        if "Final Answer:" in response:
            final = response.split("Final Answer:")[-1].strip()
            print(f"\n✅ 最终答案: {final}")
            return final

        action, action_input = parse_action(response)

        if not action or action not in TOOLS:
            print("⚠️ 未识别到工具调用，直接返回")
            return response

        print(f"\n🔧 调用工具: {action}")
        print(f"📥 输入: {action_input}")
        tool_result = TOOLS[action]["func"](action_input)
        print(f"📤 结果: {tool_result[:300]}")

        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Observation: {tool_result}\n\n请继续思考，给出下一步。"})

    return "Agent 在规定步骤内未能完成任务"

if __name__ == "__main__":
    print(run_agent("北京今天天气怎么样？"))
    print("\n" + "="*50 + "\n")
    print(run_agent("上海明天需要带伞吗？"))
