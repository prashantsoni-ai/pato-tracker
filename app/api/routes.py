# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from ..services.query_processor import QueryProcessor
from ..services.calculator import Calculator
from .dependencies import get_api_key, get_query_processor
from ..core.config import settings
from ..core.logging import logger
import pandas as pd
import tempfile
import os
import io

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def upload_page():
    """Serve the upload page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CSV Query Processor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .upload-form {
                border: 2px dashed #ccc;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }
            .upload-form:hover {
                border-color: #666;
            }
            .file-input {
                margin: 10px 0;
            }
            .submit-btn {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .submit-btn:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>CSV Query Processor</h1>
        <div class="upload-form">
            <form action="/process" method="post" enctype="multipart/form-data">
                <h2>Upload CSV File</h2>
                <p>Please upload a CSV file containing your queries</p>
                <input type="file" name="file" accept=".csv" class="file-input" required>
                <br>
                <button type="submit" class="submit-btn">Process File</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html_content

@router.post("/process")
async def process_file(
    file: UploadFile = File(...),
    query_processor: QueryProcessor = Depends(get_query_processor),
    # api_key: str = Depends(get_api_key)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    if file.size > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        contents = await file.read()
        # Read CSV file
        df_queries = pd.read_csv(
            io.BytesIO(contents),
            encoding='utf-8'  # You can adjust encoding if needed
        )
        
        # Process queries
        df_queries, queries_with_none_results, total_queries = await query_processor.process_queries(df_queries)
        
        # Perform calculations
        calculator = Calculator()
        df_queries = calculator.perform_calculations(df_queries)
        
        # Save results as CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            df_queries.to_csv(
                tmp.name,
                index=False,
                encoding='utf-8'
            )
            return FileResponse(
                tmp.name,
                media_type='text/csv',
                filename='processed_results.csv'
            )
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")