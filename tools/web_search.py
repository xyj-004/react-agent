import requests
import re

def web_search(query: str, max_results: int = 3) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        r = requests.get(
            "https://www.bing.com/search",
            params={"q": query},
            headers=headers,
            timeout=10,
            allow_redirects=True
        )
        r.encoding = "utf-8"

        def clean(s):
            s = re.sub(r'<[^>]+>', ' ', s)
            s = re.sub(r'&nbsp;', ' ', s)
            s = re.sub(r'&[a-zA-Z]+;', '', s)
            s = re.sub(r'\s+', ' ', s)
            return s.strip()

        # 按每条结果块切割
        blocks = re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>', r.text, re.DOTALL)

        results = []
        for block in blocks[:max_results]:
            title_m = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
            caption_m = re.search(r'<div class="b_caption"[^>]*>(.*?)</div>', block, re.DOTALL)

            title = clean(title_m.group(1)) if title_m else "无标题"
            abstract = clean(caption_m.group(1)) if caption_m else "无摘要"

            if title:
                results.append(f"标题: {title}\n摘要: {abstract}")

        if not results:
            return f"未找到关于 '{query}' 的结果"

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"搜索出错: {str(e)}"


if __name__ == "__main__":
    result = web_search("PyTorch是什么")
    print(result)
