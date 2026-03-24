from typing import Optional, List

from langchain_core.tools import BaseTool
from pydantic import create_model, Field

from utils.db_utils import MySqlDatabaseManager
from utils.log_utils import logger


class TableNamesTool(BaseTool):
    """获取数据库中的所有表名"""
    name: str = "get_table_names"
    description: str = "获取数据库中的所有表名,当需要了解数据库中有哪些表时使用"
    db_manager: MySqlDatabaseManager
    def __init__(self,  **kwargs)  :
        super().__init__(**kwargs)
        self.db_manager=kwargs.get('db_manager')

    def _run(self) -> str:
        try:
            tables_info=self.db_manager.get_tables_with_comments()
            result=f"数据库中共有{len(tables_info)}个表:\n\n"
            for i,table_info in enumerate(tables_info):
                table_name=table_info['table_name']
                table_comment=table_info['table_comment']
                if not table_comment or table_comment.isspace():
                    description_display="(暂无描述)"
                else:
                    description_display=table_comment
                result+=f"{i+1}.表名:{table_name}\n"
                result+=f"   描述:{description_display}\n\n"
            return result
        except Exception as e:
            logger.exception(e)
            return f"获取表名失败：{str(e)}"
    async def _arun(self) -> str:
        """
        异步获取数据库中的所有表名
        """
        return self._run()

class TableSchemaTool(BaseTool):
    """获取数据库中表的结构"""
    name: str = "get_table_schema"
    description: str = "获取数据库中表的结构,当需要了解表的字段、约束等信息时使用,输入应该是逗号分隔的表名列表,若为空则返回所有表的结构"
    db_manager: MySqlDatabaseManager
    def __init__(self, **kwargs) -> None :
        super().__init__(**kwargs)
        self.db_manager=kwargs.get('db_manager')
        self.args_schema =create_model("TableSchemaArgs", table_names=(Optional[str],Field(...,description="需要进行互联网查询的查询信息")))
    def _run(self, table_names:Optional[str] = None) -> str:
        try:
            table_list=None
            if table_names:
                table_list=[name.strip() for name in table_names.split(",") if name.strip()]
            schema_info=self.db_manager.get_table_schema(table_list)
            return schema_info if schema_info else "未找到指定的表"
        except Exception as e:
            logger.exception(e)
            return f"获取表结构失败：{str(e)}"

    async def _arun(self,table_names:Optional[str] = None) -> str:
        """
        异步获取数据库中表的结构
        """
        return self._run(table_names)

class SqlQueryExecuteTool(BaseTool):
    """执行数据库查询"""
    name: str = "execute_sql_query"
    description: str = "执行数据库查询,,输入应该是SQL查询语句,并返回查询结果"
    db_manager: MySqlDatabaseManager
    def __init__(self, **kwargs) -> None :
        super().__init__(**kwargs)
        self.db_manager=kwargs.get('db_manager')
        self.args_schema =create_model("SqlQueryExecuteArgs", query=(str,Field(...,description="需要进行SQL查询的query语句")))
    def _run(self, query:str ) -> str:
        try:
            result=self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.exception(e)
            return f"执行查询语句失败：{str(e)}"
    async def _arun(self,query:str) -> str:
        """
        异步执行数据库查询
        """
        return self._run(query)

class SqlQueryValidateTool(BaseTool):
    """进行SQL语句预编译检查,判断是否为正确的查询语句"""
    name: str = "validate_sql_query"
    description: str = "进行SQL语句预编译检查,判断是否为正确的查询语句,输入应该是SQL查询语句,并返回验证结果信息"
    db_manager: MySqlDatabaseManager
    def __init__(self, **kwargs) -> None :
        super().__init__(**kwargs)
        self.db_manager=kwargs.get('db_manager')
        self.args_schema =create_model("SqlQueryValidateArgs", query=(str,Field(...,description="需要进行SQL验证的query语句")))
    def _run(self, query:str ) -> str:
        try:
            result=self.db_manager.validate_query(query)
            return result
        except Exception as e:
            logger.exception(e)
            return f"验证SQL语句失败：{str(e)}"
    async def _arun(self,query:str) -> str:
        """
        异步验证SQL语句预编译检查
        """
        return self._run(query)

if __name__ == "__main__":
    username="root"
    password="123456"
    host="localhost"
    port=3306
    db_name="sakila"
    connection_string=f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
    db_manager=MySqlDatabaseManager(connection_string)
    # tool=TableNamesTool(db_manager=db_manager)
    # print(tool.invoke({}))
    # tool=TableSchemaTool(db_manager=db_manager)
    # print(tool.invoke({"table_names":""}))
    # tool=SqlQueryExecuteTool(db_manager=db_manager)
    # print(tool.invoke({"query":"SELECT * FROM "}))
    tool=SqlQueryValidateTool(db_manager=db_manager)
    print(tool.invoke({"query":"SELECT * FROM actor"}))