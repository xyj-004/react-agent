import requests
import json
import re
from tools.web_search import web_search
from tools.translator import translate

# ============================================================
# 工具注册表
# ============================================================
TOOLS = {
    "web_search": {"func": web_search, "desc": "用Bing搜索互联网获取最新信息。输入：搜索关键词"},
    "translate":  {"func": translate,  "desc": "将英文翻译成中文。输入：英文文本"}
}

QWEN_URL = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "/data/Newdisk/xugan/models/Qwen3-8B"

def call_qwen(messages: list) -> str:
    """调用本地 Qwen3-8B 模型"""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.6,
    }
    resp = requests.post(QWEN_URL, json=payload, timeout=60)
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    # Qwen3 会输出 <think>...</think> 思考过程，去掉它只保留实际回复
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
Action: 工具名称（只能是 web_search 或 translate）
Action Input: 传给工具的内容

当你获得足够信息后，用以下格式给出最终答案：
Thought: 我已经有足够的信息了
Final Answer: 这里写最终的中文答案

规则：
1. 每次只输出一个 Action，不要一次输出多个
2. 先用 web_search 搜索，再用 translate 翻译英文内容
3. 最终答案必须是中文
4. 不要编造信息，只根据工具返回的结果回答
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    for step in range(1, max_steps + 1):
        print(f"\n--- 第 {step} 步 ---")

        response = call_qwen(messages)
        print(f"Qwen 回复:\n{response}")

        # 检查是否给出最终答案
        if "Final Answer:" in response:
            final = response.split("Final Answer:")[-1].strip()
            print(f"\n✅ 最终答案: {final}")
            return final

        # 解析工具调用
        action, action_input = parse_action(response)

        if not action or action not in TOOLS:
            print("⚠️ 未识别到工具调用，结束")
            # 把当前回复当作最终答案
            return response

        print(f"\n🔧 调用工具: {action}")
        print(f"📥 输入: {action_input}")
        tool_result = TOOLS[action]["func"](action_input)
        print(f"📤 结果: {tool_result[:300]}")

        # 把这轮对话加入历史
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Observation: {tool_result}\n\n请继续思考，给出下一步。"})

    return "Agent 在规定步骤内未能完成任务"

if __name__ == "__main__":
    result = run_agent("PyTorch是什么？")
    print(f"\n最终返回: {result}")
