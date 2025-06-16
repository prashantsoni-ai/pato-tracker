# app/services/query_processor.py
from typing import List, Tuple
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..core.logging import logger

class QueryProcessor:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @staticmethod
    def is_sql_query(query: str) -> bool:
        return isinstance(query, str) and query.strip().lower().startswith("select")
    
    async def process_queries(self, df_queries: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], int]:
        queries_with_none_results = []
        total_queries = 0
        
        for row_idx in df_queries.index:
            for col in df_queries.columns:
                query = df_queries.at[row_idx, col]
                if self.is_sql_query(query):
                    total_queries += 1
                    try:
                        # Start a new transaction for each query
                        async with self.session.begin():
                            result = await self.session.execute(text(query))
                            result_df = pd.DataFrame(result.fetchall())
                            result_value = result_df.iloc[0, 0] if not result_df.empty else None
                            
                            if result_value is None:
                                queries_with_none_results.append(query)
                            df_queries.at[row_idx, col] = result_value
                            
                    except Exception as e:
                        logger.error(f"Error executing query at row {row_idx}, column {col}: {e}")
                        df_queries.at[row_idx, col] = None
                        queries_with_none_results.append(query)
                        # Rollback is automatic with the context manager
        
        return df_queries, queries_with_none_results, total_queries