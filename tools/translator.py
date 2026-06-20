import requests

def translate(text: str, target_lang: str = "zh") -> str:
    """
    用免费的 MyMemory API 翻译文本
    text: 要翻译的内容
    target_lang: 目标语言，zh=中文，en=英文
    """
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text[:500],
            "langpair": f"en|{target_lang}"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data["responseStatus"] == 200:
            return data["responseData"]["translatedText"]
        else:
            return f"翻译失败: {data.get('responseDetails', '未知错误')}"
    
    except Exception as e:
        return f"翻译出错: {str(e)}"


if __name__ == "__main__":
    result = translate("Python is a popular programming language.")
    print(result)
