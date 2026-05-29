import base64
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# 正确导入（适配新版包结构）
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 加载环境变量
load_dotenv()

def image_to_base64(image_path: str) -> str:
    img_bytes = Path(image_path).read_bytes()
    return base64.b64encode(img_bytes).decode("utf-8")

def generate_html_from_image(img_path: str):
    # 检查图片文件是否存在
    if not Path(img_path).exists():
        print(f"❌ 错误：图片文件不存在 - {img_path}")
        sys.exit(1)
    
    # 检查API密钥是否配置
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未找到DASHSCOPE_API_KEY环境变量")
        print("请在.env文件中配置您的API密钥")
        sys.exit(1)
    
    print(f"📷 正在处理图片：{img_path}")
    print("🔄 正在调用AI服务生成HTML...")
    
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-vl-plus",
        temperature=0.1,
        timeout=60,  # 设置60秒超时
        max_retries=2  # 最多重试2次
    )

    try:
        img_b64 = image_to_base64(img_path)
        print(f"📊 图片大小：{len(img_b64)} bytes (base64编码)")

        system_prompt = """
你是专业前端工程师。根据界面截图生成代码：
1. 1:1还原布局、配色、按钮、表格、侧边栏、顶部导航、分页；
2. 只输出完整可运行HTML+内嵌CSS，不要额外文字、注释、markdown；
3. 使用原生HTML/CSS，不引入任何外部JS和框架；
4. 严格还原圆角、边框、hover效果、文字样式与间距。
    """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=[
                {"type": "text", "text": "根据这张截图生成完整HTML代码"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                }
            ])
        ]

        response = llm.invoke(messages)
        html_code = response.content

        with open("output.html", "w", encoding="utf-8") as f:
            f.write(html_code)
        
        print("✅ 生成完成：output.html")
        print(f"📄 HTML文件大小：{Path('output.html').stat().st_size} bytes")
        
    except Exception as e:
        print(f"❌ 生成失败：{str(e)}")
        print("\n可能的原因：")
        print("1. 网络连接问题，请检查网络状态")
        print("2. API密钥无效或已过期")
        print("3. API服务暂时不可用")
        print("4. 请求超时，请稍后重试")
        sys.exit(1)

if __name__ == "__main__":
    IMAGE_PATH = "ui_screenshot.png"
    generate_html_from_image(IMAGE_PATH)