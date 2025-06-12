import pandas as pd
from ..core.logging import logger

class Calculator:
    @staticmethod
    def perform_calculations(df_queries: pd.DataFrame) -> pd.DataFrame:
        calculations = {
            9: (6, 7, 8),   # Row 9: Row 6 - (Row 7 + Row 8)
            30: (26, 28),   # Row 30: Row 26 + Row 28
            31: (27, 29),   # Row 31: Row 27 + Row 29
            36: (34, 35),   # Row 36: Row 34 + Row 35
            37: (31, 36),   # Row 37: Row 31 - Row 36
            41: (39, 40)    # Row 41: Row 39 + Row 40
        }
        
        for column in df_queries.columns[1:]:
            for target_row, rows in calculations.items():
                try:
                    if target_row >= len(df_queries):
                        logger.warning(f"Target row {target_row} out of bounds")
                        continue
                    
                    if len(rows) == 3:
                        row1, row2, row3 = rows
                        if all(row < len(df_queries) for row in [row1, row2, row3]):
                            value1 = pd.to_numeric(df_queries.loc[row1, column], errors='coerce')
                            value2 = pd.to_numeric(df_queries.loc[row2, column], errors='coerce')
                            value3 = pd.to_numeric(df_queries.loc[row3, column], errors='coerce')
                            result = value1 - (value2 + value3)
                            df_queries.loc[target_row, column] = result
                    else:
                        row1, row2 = rows
                        if all(row < len(df_queries) for row in [row1, row2]):
                            value1 = pd.to_numeric(df_queries.loc[row1, column], errors='coerce')
                            value2 = pd.to_numeric(df_queries.loc[row2, column], errors='coerce')
                            
                            if target_row == 37:
                                result = value1 - value2
                            else:
                                result = value1 + value2
                            
                            df_queries.loc[target_row, column] = result
                except Exception as e:
                    logger.error(f"Calculation error for row {target_row}, column {column}: {e}")
                    df_queries.loc[target_row, column] = None
        
        return df_queries
