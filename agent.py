from tools.web_search import web_search
from tools.translator import translate
import re

TOOLS = {
    "web_search": {"func": web_search, "desc": "用Bing搜索互联网获取最新信息"},
    "translate":  {"func": translate,  "desc": "将英文翻译成中文"}
}

def parse_action(text: str):
    action, action_input = None, None
    for line in text.strip().split("\n"):
        if line.startswith("Action:"):
            action = line.replace("Action:", "").strip()
        if line.startswith("Action Input:"):
            action_input = line.replace("Action Input:", "").strip()
    return action, action_input

def extract_keyword(question: str) -> str:
    q = re.sub(r'^(what is|what are|how to|why is|who is|tell me about)', '', question, flags=re.IGNORECASE)
    q = re.sub(r'\?$', '', q).strip()
    return q + " 介绍"

def extract_best_snippet(search_result: str) -> str:
    """从搜索结果里取最有价值的摘要（第一条非空摘要）"""
    blocks = search_result.split("---")
    for block in blocks:
        lines = block.strip().split("\n")
        for line in lines:
            if line.startswith("摘要:"):
                snippet = line.replace("摘要:", "").strip()
                # 去掉 HTML 实体
                snippet = re.sub(r'&#\d+;', '', snippet)
                snippet = re.sub(r'&[a-zA-Z]+;', '', snippet)
                if len(snippet) > 20:
                    return snippet
    return search_result[:200]

def call_llm(messages: list, step: int) -> str:
    user_q = messages[1]["content"]

    if step == 1:
        keyword = extract_keyword(user_q)
        return f"""Thought: 提取关键词进行搜索
Action: web_search
Action Input: {keyword}"""

    if step == 2:
        search_result = ""
        for msg in messages:
            if msg["role"] == "user" and "Observation:" in msg["content"]:
                search_result = msg["content"].replace("Observation:", "").strip()
                break
        best = extract_best_snippet(search_result)
        return f"""Thought: 取最佳摘要翻译成中文
Action: translate
Action Input: {best}"""

    if step == 3:
        observations = []
        for msg in messages:
            if msg["role"] == "user" and "Observation:" in msg["content"]:
                observations.append(msg["content"].replace("Observation:", "").strip())
        # 搜索结果 + 翻译结果合并
        search_res = observations[0] if len(observations) > 0 else ""
        translated  = observations[1] if len(observations) > 1 else ""
        
        # 从搜索结果提取标题列表
        titles = re.findall(r'标题: (.+)', search_res)
        title_list = "\n".join([f"  - {t}" for t in titles[:3]])
        
        final = f"【翻译摘要】{translated}\n\n【相关来源】\n{title_list}"
        return f"""Thought: 整合信息给出最终答案
Final Answer: {final}"""

    return "Final Answer: 无法完成任务"

def run_agent(user_question: str) -> str:
    print(f"\n{'='*50}")
    print(f"用户问题: {user_question}")
    print(f"{'='*50}")

    messages = [
        {"role": "system", "content": "你是智能助手"},
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
    result = run_agent("What is PyTorch?")
    print(f"\n最终返回: {result}")
