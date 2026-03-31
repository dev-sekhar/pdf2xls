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
    """Takes a list of dataframes and renders them safely into an Excel workbook."""
    try:
        with pd.ExcelWriter(output_path_or_buffer, engine='openpyxl') as writer:
            for sheet_name, df in all_tables:
                # Final safety check on sheet names to prevent corrupting the workbook
                safe_sheet_name = re.sub(r'[\[\]:\*\?/\\]', '', sheet_name).strip()[:31] or "Unnamed_Sheet"
                df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    except PermissionError:
        logger.error(f"Permission denied: Cannot write to targets. Is the Excel file currently open?")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while saving Excel file: {e}")
        raise
