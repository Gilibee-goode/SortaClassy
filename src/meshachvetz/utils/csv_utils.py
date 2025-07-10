"""
CSV utilities for Excel-compatible output with Hebrew text support.

This module provides utilities for writing CSV files that properly display Hebrew
text in Microsoft Excel by using UTF-8 encoding with BOM (Byte Order Mark).
"""

import csv
import os
from typing import List, Any, TextIO
from pathlib import Path


def open_excel_csv(file_path: str, mode: str = 'w') -> TextIO:
    """
    Open a CSV file with Excel-compatible UTF-8 BOM encoding.
    
    This ensures Hebrew text displays correctly in Excel by adding the UTF-8 
    Byte Order Mark that Excel expects for proper Unicode text rendering.
    
    Args:
        file_path: Path to the CSV file
        mode: File opening mode (default: 'w')
        
    Returns:
        File handle with proper encoding for Excel compatibility
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Open with UTF-8 BOM encoding for Excel compatibility
    return open(file_path, mode, newline='', encoding='utf-8-sig')


def write_excel_csv(file_path: str, rows: List[List[Any]], headers: List[str] = None) -> None:
    """
    Write CSV data to file with Excel-compatible UTF-8 BOM encoding.
    
    Args:
        file_path: Path to save the CSV file
        rows: List of row data (each row is a list of values)
        headers: Optional header row to write first
    """
    with open_excel_csv(file_path, 'w') as f:
        writer = csv.writer(f)
        
        # Write headers if provided
        if headers:
            writer.writerow(headers)
        
        # Write data rows
        writer.writerows(rows)


class ExcelCsvWriter:
    """
    Context manager for writing Excel-compatible CSV files with Hebrew support.
    
    Usage:
        with ExcelCsvWriter('output.csv') as writer:
            writer.writerow(['שם', 'כיתה', 'ציון'])
            writer.writerow(['יוסי', 'א1', '85'])
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the Excel CSV writer.
        
        Args:
            file_path: Path to the CSV file to write
        """
        self.file_path = file_path
        self.file_handle = None
        self.csv_writer = None
    
    def __enter__(self):
        """Enter context manager and return CSV writer."""
        self.file_handle = open_excel_csv(self.file_path, 'w')
        self.csv_writer = csv.writer(self.file_handle)
        return self.csv_writer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close file."""
        if self.file_handle:
            self.file_handle.close()


def create_excel_csv_writer(file_path: str) -> tuple[TextIO, csv.writer]:
    """
    Create a file handle and CSV writer for Excel-compatible output.
    
    Returns a tuple of (file_handle, csv_writer) that must be closed manually.
    For automatic cleanup, use ExcelCsvWriter context manager instead.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (file_handle, csv_writer)
    """
    file_handle = open_excel_csv(file_path, 'w')
    csv_writer = csv.writer(file_handle)
    return file_handle, csv_writer


def is_hebrew_text(text: str) -> bool:
    """
    Check if text contains Hebrew characters.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains Hebrew characters
    """
    if not isinstance(text, str):
        return False
    
    # Hebrew Unicode range: U+0590 to U+05FF
    for char in text:
        if '\u0590' <= char <= '\u05FF':
            return True
    
    return False


def detect_hebrew_in_file(file_path: str) -> bool:
    """
    Detect if a CSV file contains Hebrew text.
    
    Args:
        file_path: Path to CSV file to check
        
    Returns:
        True if Hebrew characters are found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines to check for Hebrew
            for i, line in enumerate(f):
                if i > 10:  # Check first 10 lines only
                    break
                if is_hebrew_text(line):
                    return True
        return False
    except Exception:
        return False


def convert_csv_to_excel_format(input_file: str, output_file: str = None) -> str:
    """
    Convert an existing CSV file to Excel-compatible format with UTF-8 BOM.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path for output file (defaults to input_file if not provided)
        
    Returns:
        Path to the converted file
    """
    import pandas as pd
    
    if output_file is None:
        output_file = input_file
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Save with UTF-8 BOM encoding for Excel compatibility
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    return output_file 