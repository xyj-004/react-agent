from tools.web_search import web_search
from tools.translator import translate

TOOLS = {
    "web_search": {
        "func": web_search,
        "desc": "用Bing搜索互联网获取最新信息。输入：搜索关键词（用中文）"
    },
    "translate": {
        "func": translate,
        "desc": "将英文翻译成中文。输入：需要翻译的英文文本"
    }
}

def parse_action(text: str):
    action = None
    action_input = None
    for line in text.strip().split("\n"):
        if line.startswith("Action:"):
            action = line.replace("Action:", "").strip()
        if line.startswith("Action Input:"):
            action_input = line.replace("Action Input:", "").strip()
    return action, action_input

def call_llm(messages: list, step: int) -> str:
    user_q = messages[1]["content"]

    if step == 1:
        # 把问题翻译成中文关键词再搜索
        translated_q = translate(user_q)
        return f"""Thought: 我需要先把问题翻译成中文，再用中文搜索
Action: web_search
Action Input: {translated_q}"""

    if step == 2:
        search_result = ""
        for msg in messages:
            if msg["role"] == "user" and "Observation:" in msg["content"]:
                search_result = msg["content"].replace("Observation:", "").strip()
                break
        to_translate = search_result[:400]
        return f"""Thought: 我得到了搜索结果，整理成最终答案
Action: translate
Action Input: {to_translate}"""

    if step == 3:
        observations = []
        for msg in messages:
            if msg["role"] == "user" and "Observation:" in msg["content"]:
                observations.append(msg["content"].replace("Observation:", "").strip())
        result = observations[-1] if observations else "暂无结果"
        return f"""Thought: 我现在有足够信息了
Final Answer: {result}"""

    return "Final Answer: 无法完成任务"

def run_agent(user_question: str) -> str:
    print(f"\n{'='*50}")
    print(f"用户问题: {user_question}")
    print(f"{'='*50}")

    tools_desc = "\n".join([f"- {name}: {info['desc']}" for name, info in TOOLS.items()])
    system_prompt = f"""你是一个智能助手，必须按顺序使用工具：
1. 先用 web_search 搜索（用中文关键词）
2. 再用 translate 整理结果
3. 最后给出中文答案

可用工具：
{tools_desc}
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    for step in range(1, 4):
        print(f"\n--- 第 {step} 步 ---")
        response = call_llm(messages, step)
        print(f"AI 回复:\n{response}")

        if "Final Answer:" in response:
            final = response.split("Final Answer:")[-1].strip()
            print(f"\n✅ 最终答案: {final}")
            return final

        action, action_input = parse_action(response)
        if not action or action not in TOOLS:
            break

        print(f"\n🔧 调用工具: {action}")
        print(f"📥 输入: {action_input}")
        tool_result = TOOLS[action]["func"](action_input)
        print(f"📤 结果: {tool_result[:300]}")

        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Observation: {tool_result}"})

    return "Agent 未能完成任务"

if __name__ == "__main__":
    result = run_agent("What is the latest version of Python?")
    print(f"\n最终返回: {result}")
