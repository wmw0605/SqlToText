# 补充必要的导入
from utils.model_init import qwen3,qwen3_vl
from langchain.agents import create_agent
from langchain_core.tools import tool


# 定义天气查询工具
@tool
def get_weather(location: str):
    """
    获取指定城市的天气信息

    参数:
        location: 城市名称（如"北京"、"上海"）

    返回:
        str: 该城市的天气描述，包含温度、天气状况等
    """
    # 模拟返回天气数据，实际场景可替换为真实天气API调用
    return f"{location}的天气是25度，天气晴朗，微风3级"





# 1. 创建Agent（核心逻辑）
agent = create_agent(
    model=qwen3_vl,
    # tools=[get_weather]

)



# 3. 调用Agent查询天气（示例）
if __name__ == "__main__":
    # 方式1：传入HumanMessage（推荐）
    result = agent.invoke({
        "messages": [{"role":"user","content":"北京的天气"}]
    })

    # 打印最终结果
    print("\n===== 最终回答 =====")
    print(result["messages"][-1].content)

    # 方式2：直接传入文本（简化版）
    # result = agent_executor.invoke({"input": "上海的天气如何？"})
    # print(result["output"])
