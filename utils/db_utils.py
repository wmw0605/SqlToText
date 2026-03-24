from typing import List, Optional
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SAWarning
import warnings
from utils.log_utils import logger

#  suppress the SAWarning about unrecognized column types
warnings.filterwarnings('ignore', category=SAWarning, message="Did not recognize type 'geometry' of column")


class MySqlDatabaseManager:

    def __init__(self,connection_string):
        self.engine = create_engine(connection_string,pool_recycle=3600,pool_size=5)

    def get_table_names(self) -> list[str]:
        """
        获取数据库中所有表的名称
        
        Returns:
            list[str]: 包含所有表名的列表
            
        Raises:
            ValueError: 当获取表名失败时抛出，包含具体错误信息
        """
        try:
            # 创建数据库检查器实例，用于获取数据库结构信息
            inspector = inspect(self.engine)
            # 获取并返回所有表名
            return inspector.get_table_names()
        except Exception as e:
            # 记录详细异常信息
            logger.exception(e)
            # 抛出带有错误信息的ValueError
            raise ValueError(f"获取表名失败：{str(e)}")

    def get_tables_with_comments(self) -> List[dict]:
        """
        获取数据库中所有表的信息，包括注释

        Returns:
            List[dict]: 包含表名和注释的字典列表，每个字典包含 'table_name' 和 'table_comment' 键

        Raises:
            ValueError: 当获取表信息失败时抛出，包含具体错误信息
        """
        try:
            # 创建数据库检查器实例
            inspector = inspect(self.engine)
            # 获取所有表名
            table_names = inspector.get_table_names()
            logger.info(f"获取到 {len(table_names)} 个表")
            tables_with_comments = []

            # 遍历表名，获取注释信息
            for table_name in table_names:
                try:
                    # 获取表的注释信息
                    table_comment = inspector.get_table_comment(table_name)["text"]
                    # 即使没有注释也添加到结果中
                    tables_with_comments.append({
                        "table_name": table_name,
                        "table_comment": table_comment or ""
                    })
                except Exception as e:
                    logger.warning(f"获取表 {table_name} 的注释失败: {str(e)}")
                    # 即使获取注释失败，也添加表名到结果中
                    tables_with_comments.append({
                        "table_name": table_name,
                        "table_comment": ""
                    })

            logger.info(f"返回 {len(tables_with_comments)} 个表的信息")
            return tables_with_comments
        except Exception as e:
            # 记录详细异常信息
            logger.exception(e)
            # 抛出带有错误信息的ValueError
            raise ValueError(f"获取带有注释的表失败：{str(e)}")

    def get_table_schema(self,table_names:Optional[List[str]]=None) -> str:
        """
        获取指定表的模式信息(包含字段、索引、约束等信息)
        
        Args:
            table_names: 表名列表，如果为空则获取所有表的模式信息
            
        Returns:
            str: 包含表模式信息的字符串，格式清晰易读
            
        Raises:
            ValueError: 当获取表模式信息失败时抛出，包含具体错误信息
        """
        try:
            # 创建数据库检查器实例
            inspector = inspect(self.engine)
            
            # 如果未指定表名，则获取所有表名
            if table_names is None:
                table_names = inspector.get_table_names()
            elif not isinstance(table_names, list):
                table_names = [table_names]
            schema_info = []
            
            # 遍历每个表，获取其模式信息
            for table_name in table_names:
                schema_info.append(f"\n=== 表: {table_name} ===")
                
                # 获取表的注释
                table_comment = inspector.get_table_comment(table_name)["text"]
                if table_comment:
                    schema_info.append(f"注释: {table_comment}")
                
                # 获取表的字段信息
                schema_info.append("\n字段信息:")
                columns = inspector.get_columns(table_name)
                for column in columns:
                    column_info = f"- {column['name']}: {column['type']}"
                    if column['nullable']:
                        column_info += " (NULL)"
                    if column.get('default') is not None:
                        column_info += f" (默认: {column['default']})"
                    # 获取字段注释（如果有）
                    if 'comment' in column and column['comment']:
                        column_info += f" -- {column['comment']}"
                    schema_info.append(column_info)
                
                # 获取表的索引信息
                schema_info.append("\n索引信息:")
                indexes = inspector.get_indexes(table_name)
                for index in indexes:
                    index_info = f"- {index['name']}: {', '.join(index['column_names'])}"
                    if index['unique']:
                        index_info += " (唯一)"
                    schema_info.append(index_info)
                
                # 获取表的外键信息
                schema_info.append("\n外键信息:")
                foreign_keys = inspector.get_foreign_keys(table_name)
                for fk in foreign_keys:
                    fk_info = f"- {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}"
                    schema_info.append(fk_info)
                
                # 获取表的约束信息
                schema_info.append("\n约束信息:")
                # 注意：SQLAlchemy的inspect工具没有直接获取所有约束的方法
                # 这里我们获取主键和唯一约束作为示例
                # 主键约束
                primary_keys = inspector.get_pk_constraint(table_name)
                if primary_keys['constrained_columns']:
                    schema_info.append(f"- 主键: {', '.join(primary_keys['constrained_columns'])}")
                # 唯一约束
                unique_constraints = inspector.get_unique_constraints(table_name)
                for uc in unique_constraints:
                    if uc.get('constrained_columns'):
                        schema_info.append(f"- 唯一约束: {uc['name']} ({', '.join(uc['constrained_columns'])})")
                    elif uc.get('column_names'):
                        schema_info.append(f"- 唯一约束: {uc['name']} ({', '.join(uc['column_names'])})")
            
            # 将所有信息合并为一个字符串并返回
            return '\n'.join(schema_info)
        except Exception as e:
            # 记录详细异常信息
            logger.exception(e)
            # 抛出带有错误信息的ValueError
            raise ValueError(f"获取表模式信息失败：{str(e)}")

    def execute_query(self, query: str) -> str:
        """
        执行SQL查询并返回结果，只允许执行查询语句

        Args:
            query: SQL查询语句

        Returns:
            查询结果的字符串表示，如果不是查询语句则返回提示信息

        Raises:
            Exception: 如果执行查询时出错
        """
        # 验证是否为查询语句（以SELECT开头，不区分大小写）
        if not query.strip().upper().startswith('SELECT'):
            return "只允许执行查询语句（以SELECT开头）"

        try:
            # 导入text函数
            from sqlalchemy import text
            
            # 使用engine创建连接并执行查询
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                results = result.fetchall()

                # 获取列名
                column_names = result.keys()

                # 检查结果是否为空
                if not results:
                    return "查询结果为空"

                # 构建结果字符串
                result_str = "| " + " | ".join(column_names) + " |\n"
                result_str += "| " + " | ".join(["---"] * len(column_names)) + " |\n"

                for row in results:
                    row_str = "| " + " | ".join(str(item) for item in row) + " |\n"
                    result_str += row_str

                return result_str

        except Exception as e:
            # 检查是否是表不存在的错误
            error_message = str(e)
            if "doesn't exist" in error_message:
                return "表不存在"
            # 其他错误仍然抛出
            raise Exception(f"执行查询时出错: {str(e)}")
            
    def execute_statement(self, query: str) -> int:
        """
        执行SQL语句（如INSERT、UPDATE、DELETE）并返回受影响的行数

        Args:
            query: SQL语句

        Returns:
            int: 受影响的行数

        Raises:
            Exception: 如果执行语句时出错
        """
        try:
            # 导入text函数
            from sqlalchemy import text
            
            # 使用engine创建连接并执行语句
            with self.engine.connect() as conn:
                with conn.begin() as transaction:
                    result = conn.execute(text(query))
                    transaction.commit()
                    return result.rowcount

        except Exception as e:
            raise Exception(f"执行语句时出错: {str(e)}")

    def validate_query(self, query: str) -> str:
        """
        验证SQL查询语句是否正确，使用实际执行来检测语法错误

        Args:
            query: SQL查询语句

        Returns:
            str: 返回"语法正确"或"语法错误"
        """
        # 验证是否为查询语句（以SELECT开头，不区分大小写）
        if not query.strip().upper().startswith('SELECT'):
            return "语法错误"

        try:
            # 导入text函数
            from sqlalchemy import text

            # 使用engine创建连接并尝试执行查询（但只获取前0行，不实际返回数据）
            with self.engine.connect() as conn:
                # 尝试执行查询，使用limit 0来避免返回数据
                # 这样可以检测语法错误，但不会实际执行查询逻辑
                test_query = query + " LIMIT 0"
                result = conn.execute(text(test_query))
                # 如果执行成功，说明语法正确
                return "语法正确"

        except Exception as e:
            # 如果发生异常，说明SQL语句有问题
            return "语法错误"

if __name__=="__main__":
    host="localhost"
    port=3306
    database="sakila"
    username="root"
    password="123456"
    manager=MySqlDatabaseManager(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")
    print(manager.get_table_schema(["actor","city"]))
