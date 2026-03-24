from typing import List
from src.tools.mysql_tools import TableNamesTool, TableSchemaTool, SqlQueryExecuteTool, SqlQueryValidateTool
from utils.model_init import qwen3
from langchain.agents import create_agent
from langchain_core.tools import tool, BaseTool
from utils.db_utils import MySqlDatabaseManager

def get_tools(username:str,password:str,host:str,port:int,database:str)->List[BaseTool]:
    connect_str=f"mysql://{username}:{password}@{host}:{port}/{database}"
    database_manager = MySqlDatabaseManager(connect_str)
    return [TableNamesTool(db_manager=database_manager),
            TableSchemaTool(db_manager=database_manager),
            SqlQueryExecuteTool(db_manager=database_manager),
            SqlQueryValidateTool(db_manager=database_manager)]

system_prompt="""
    你是一个专门用于查询数据库的助手,你可以执行SQL查询语句,并返回查询结果
    
    给定一个输入问题,你需要按照以下步骤进行处理:
    1. 先检查数据库中是否存在相关的表
    2. 如果存在,则根据问题的描述,生成一个正确的{dialect}查询语句,最好是select语句。
    3. 执行SQL语句,并查询数据库
    4. 返回查询结果
    
    除非用户明确指定要获取的具体示例数量,否则始终将查询结果限制为最多{top_k}条。
    
    你可以通过相关列对结果进行排序,以返回数据库中最有意义的示例。
    永远不要查询特定表的所有数据,而只查询与问题相关的数据。
    
    在执行查询前,你必须仔细检查查询语句。如果在查询语句中包含错误,请重写查询语句再次尝试。
    
    绝对不要对数据库执行任何数据操作语言,如INSERT、UPDATE、DELETE等。
    
    开始处理问题时,你应该始终先检查数据库中有哪些表可以用于查询。不要跳过这一步。
    
    然后,你应该查询最相关的表的结构,以了解表的列和数据类型。
    然后,你应该根据问题的描述,生成一个正确的SQL查询语句,最好是select语句。
    最后,你应该执行查询语句,并返回查询结果。
    """.format(
    dialect="MySQL",
    top_k=5
)
agent=create_agent(
    model=qwen3,
    tools=get_tools("root","123456","localhost",3306,"erp_nightmare_db"),
    system_prompt=system_prompt
)

for step in agent.stream(
    input={'messages':[{"role":"user","content":"员工小李的工资是多少？他的全名就叫“员工小李”。"}]},
    stream_mode="values"
):
    step["messages"][-1].pretty_print()