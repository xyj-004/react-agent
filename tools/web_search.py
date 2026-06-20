import requests
import re

def web_search(query: str, max_results: int = 5) -> str:
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
            s = re.sub(r'&#\d+;', '', s)
            s = re.sub(r'&[a-zA-Z]+;', '', s)
            s = re.sub(r'\s+', ' ', s)
            return s.strip()

        blocks = re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>', r.text, re.DOTALL)

        # 提取关键词（去掉"介绍"等后缀）
        keywords = [w.lower() for w in query.replace("介绍", "").replace("是什么", "").split() if len(w) > 1]

        results = []
        for block in blocks:
            title_m = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
            caption_m = re.search(r'<div class="b_caption"[^>]*>(.*?)</div>', block, re.DOTALL)

            title = clean(title_m.group(1)) if title_m else ""
            abstract = clean(caption_m.group(1)) if caption_m else ""
            combined = (title + " " + abstract).lower()

            # 过滤：至少有一个关键词出现在结果里
            if any(kw in combined for kw in keywords):
                results.append(f"标题: {title}\n摘要: {abstract}")

            if len(results) >= max_results:
                break

        if not results:
            # 没过滤到，返回前3条原始结果
            for block in blocks[:3]:
                title_m = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
                caption_m = re.search(r'<div class="b_caption"[^>]*>(.*?)</div>', block, re.DOTALL)
                title = clean(title_m.group(1)) if title_m else ""
                abstract = clean(caption_m.group(1)) if caption_m else ""
                if title:
                    results.append(f"标题: {title}\n摘要: {abstract}")

        return "\n\n---\n\n".join(results) if results else f"未找到关于 '{query}' 的结果"

    except Exception as e:
        return f"搜索出错: {str(e)}"


if __name__ == "__main__":
    result = web_search("PyTorch 介绍")
    print(result)
