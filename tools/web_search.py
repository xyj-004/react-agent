from ddgs import DDGS

def web_search(query: str, max_results: int = 3) -> str:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"标题: {r['title']}\n摘要: {r['body']}\n链接: {r['href']}")
        
        if not results:
            return "没有找到相关搜索结果"
        
        return "\n\n---\n\n".join(results)
    
    except Exception as e:
        return f"搜索出错: {str(e)}"


if __name__ == "__main__":
    result = web_search("Python最新版本")
    print(result)
