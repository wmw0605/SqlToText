from typing import Callable
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import sys
from utils.model_init import qwen3,qwen3_vl
from langchain.messages import HumanMessage
import base64

json_schema = {
    "title": "movie_poster",
    "description": "电影海报的详细信息",
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "海报中的电影名称"},
        "year": {"type": "integer", "description": "电影上映年份"},
        "director": {"type": "string", "description": "导演（英文名字）"},
        "rating": {"type": "number", "description": "电影评分"},
        "genre": {"type": "string", "description": "电影类型"},
        "image_desc": {"type": "string", "description": "海报的视觉描述（颜色、构图、主角等）"}
    },
    "required": ["title", "year", "director", "rating", "genre", "image_desc"]
}

# 1. 将你的 JSON Schema 转换为 Pydantic 类
class MoviePosterInfo(BaseModel):
    title: str = Field(description="海报中的电影名称")
    year: int = Field(description="电影上映年份")
    director: str = Field(description="导演（英文名字）")
    rating: float = Field(description="电影评分")
    genre: str = Field(description="电影类型")
    image_desc: str = Field(description="海报的视觉描述（颜色、构图、主角等）")

# 2. 定义一个工具，告诉 Agent 使用这个工具来输出最终结果
@tool(args_schema=json_schema)
def save_poster_info(title: str, year: int, director: str, rating: float, genre: str, image_desc: str):
    """当你看完电影海报并提取出所有信息后，必须调用此工具保存数据。"""
    # 这个工具内部其实什么都不用做，我们只是为了截获 Agent 传过来的参数
    return {
        "title": title, "year": year, "director": director,
        "rating": rating, "genre": genre, "image_desc": image_desc
    }


# ---------------------- 工具函数：图片转Base64 ----------------------
def image_to_base64(image_path):
    """将本地图片转换为Base64编码（Ollama多模态API要求）"""
    with open(image_path, "rb") as f:
        # 编码为base64字符串，去除换行符
        base64_str = base64.b64encode(f.read()).decode("utf-8").replace("\n", "")
    return base64_str


# ---------------------- 构造图文混合请求 ----------------------
# 1. 本地图片路径
image_path = "../../static/2.jpg"
# 2. 转换为Base64
image_base64 = image_to_base64(image_path)
messages = [
    HumanMessage(
        content=[
            {"type": "text", "text": "请分析图片里的电影海报信息，并必须调用 save_poster_info 工具保存结果。"},
            # ollama 要求这里的 type 必须是 "image_url"，且键名也要用 "image"
            {"type": "image_url", "image_url": image_base64}
        ]
    )
]




@wrap_model_call
async def switch_model(request: ModelRequest, handler: Callable) -> ModelResponse:
    flag = False

    # 获取消息内容并确保它是列表（为了代码的健壮性最好加个类型判断）
    content = request.messages[0].content
    if isinstance(content, list):
        for item in content:
            # 使用 .get() 更安全，防止某些字典没有 "type" 键导致报错
            if item.get("type") == "image":
                flag = True
                break  # 找到图片就不需要继续遍历了

    if flag:
        # 💡 核心修改：使用 override 方法创建一个包含新属性的 request 副本
        request = request.override(
            model=qwen3_vl,
            messages=messages
        )

    return await handler(request)
# ---------------------- 初始化多模态模型 ----------------------


# ---------------------- 定义结构化输出Schema（示例：分析图片中的电影海报） ----------------------

# 绑定结构化输出
model_with_struct = qwen3.with_structured_output(
    json_schema,
    include_raw=True
)



# 3. 构造符合 Qwen/DashScope 格式的 HumanMessage
request_messages = [
    HumanMessage(
        content=[
            {"type": "text", "text": "请分析图片里的电影海报信息"},
            # Qwen 要求这里的 type 必须是 "image"，且键名也要用 "image"
            {"type": "image", "image": f"data:image/jpeg;base64,{image_base64}"}
        ]
    )
]

# 或者，直接使用字典列表（LangChain 也能自动解析）：
# request_messages = [
#     {"role": "user", "content": [
#         {"text": "请分析这张电影海报，提取信息。"},
#         {"image": f"data:image/jpeg;base64,{image_base64}"}
#     ]}
# ]
agent = create_agent(
    model=qwen3,
    # middleware=[switch_model],
)



# print("\n===== 最终回答 =====")
# result=agent.invoke({"messages": request_messages})
# print(result["messages"][-1].content)
# for chunk, metadata in agent.stream(
#         {"messages": request_messages},
#         stream_mode="messages"
# ):
#     if chunk.type == "ai" or chunk.__class__.__name__ == "AIMessageChunk":
#
#         # 1. 捕获普通的文本流（如果大模型在调用工具前后想说些废话）
#         if chunk.content and isinstance(chunk.content, str):
#             sys.stdout.write(chunk.content)
#             sys.stdout.flush()
#
#         # 2. 💡 核心修复：捕获工具调用的 JSON 参数流（也就是你的结构化输出）
#         if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
#             for tc_chunk in chunk.tool_call_chunks:
#                 # tc_chunk 是一个字典，里面有 'name', 'args', 'id' 等字段
#                 # 我们只需要打印 'args' (即正在生成的 JSON 字符串片段)
#                 if "args" in tc_chunk:
#                     sys.stdout.write(tc_chunk["args"])
#                     sys.stdout.flush()
#
# print()  # 最后换行


