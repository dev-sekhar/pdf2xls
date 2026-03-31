import pandas as pd
import re

"""
src/exporter.py
---------------
Purpose: Takes extracted, fully parsed data and safely compiles it into
Microsoft Excel `.xlsx` workbooks while handling OS-level save constraints.
"""

from src.config import get_logger

logger = get_logger(__name__)

def save_tables_to_excel(all_tables, output_path_or_buffer):
    """Takes extracted, fully parsed data and safely compiles it into
    Microsoft Excel `.xlsx` workbooks while handling OS-level save constraints.
    """
    try:
        with pd.ExcelWriter(output_path_or_buffer, engine='openpyxl') as writer:
            for sheet_name, df in all_tables:
                # Final safety check on sheet names to prevent corrupting the workbook
                safe_sheet_name = re.sub(r'[\[\]:\*\?/\\]', '', sheet_name).strip()[:31] or "Unnamed_Sheet"
                
                # Streamlit specifically requires strictly unique column placeholders which forced "Unnamed",
                # but Excel does not care. Clean out the artificial helpers so the exported file looks perfectly clean!
                export_df = df.copy()
                clean_cols = []
                for col in export_df.columns:
                    col_str = str(col)
                    if col_str == "Unnamed" or re.match(r'^Unnamed_\d+$', col_str):
                        clean_cols.append("")
                    else:
                        clean_cols.append(col_str)
                
                export_df.columns = clean_cols
                export_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    except PermissionError:
        logger.error(f"Permission denied: Cannot write to targets. Is the Excel file currently open?")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while saving Excel file: {e}")
        raise
