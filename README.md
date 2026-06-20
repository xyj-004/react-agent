# ReAct Agent

基于 ReAct 机制的智能 Agent，支持网页搜索 + 翻译两个工具。

## 项目结构
agent_project/

├── app.py          # Flask API 接口

├── agent.py        # ReAct Agent 核心逻辑

└── tools/

├── web_search.py   # 网页搜索工具

└── translator.py   # 翻译工具
## 启动方式
```bash
conda activate agent_project
python app.py
```

## 接口使用
```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is PyTorch?"}'
```
