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

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def upload_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Query Sheet Processor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 2px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 20px;
                transition: border-color 0.3s;
            }
            .upload-area:hover {
                border-color: #007bff;
            }
            .upload-area.dragover {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            input[type="file"] {
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                width: 100%;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
                margin-top: 10px;
            }
            button:hover {
                background-color: #0056b3;
            }
            button:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            .progress {
                width: 100%;
                height: 20px;
                background-color: #f0f0f0;
                border-radius: 10px;
                overflow: hidden;
                margin: 20px 0;
                display: none;
            }
            .progress-bar {
                height: 100%;
                background-color: #007bff;
                width: 0%;
                transition: width 0.3s;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 5px;
                display: none;
            }
            .success {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            .download-link {
                display: inline-block;
                margin-top: 10px;
                padding: 8px 15px;
                background-color: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            .download-link:hover {
                background-color: #218838;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 PATO TRACKER PROCESSOR (MAIN SHEET)</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Upload your CSV file containing SQL queries to process them automatically
            </p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <div>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="#ccc" style="margin-bottom: 10px;">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                    </div>
                    <p>Drag and drop your CSV file here, or click to browse</p>
                    <input type="file" id="fileInput" name="file" accept=".csv" required>
                </div>
                
                <div class="progress" id="progressContainer">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                
                <button type="submit" id="submitBtn">Process Queries</button>
            </form>
            
            <div class="result" id="result"></div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const form = document.getElementById('uploadForm');
            const submitBtn = document.getElementById('submitBtn');
            const progressContainer = document.getElementById('progressContainer');
            const progressBar = document.getElementById('progressBar');
            const result = document.getElementById('result');

            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    updateFileName(files[0].name);
                }
            });

            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    updateFileName(e.target.files[0].name);
                }
            });

            function updateFileName(fileName) {
                const p = uploadArea.querySelector('p');
                p.textContent = `Selected: ${fileName}`;
            }

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const file = fileInput.files[0];
                
                if (!file) {
                    showResult('Please select a file', 'error');
                    return;
                }
                
                formData.append('file', file);
                
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                progressContainer.style.display = 'block';
                result.style.display = 'none';
                
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 30;
                    if (progress > 90) progress = 90;
                    progressBar.style.width = progress + '%';
                }, 500);
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });
                    
                    clearInterval(progressInterval);
                    progressBar.style.width = '100%';
                    
                    if (response.ok) {
                        const data = await response.json();
                        showResult(
                            `Processing completed successfully!✅<br>
                             Processed ${data.total_queries} queries<br>
                            ⚠️ ${data.failed_queries} queries failed<br>
                            <a href="/download/${data.filename}" class="download-link">📥 Download Results</a>`,
                            'success'
                        );
                    } else {
                        const errorData = await response.json();
                        showResult(`❌ Error: ${errorData.detail}`, 'error');
                    }
                } catch (error) {
                    clearInterval(progressInterval);
                    showResult(`❌ Network error: ${error.message}`, 'error');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Process Queries';
                    setTimeout(() => {
                        progressContainer.style.display = 'none';
                        progressBar.style.width = '0%';
                    }, 1000);
                }
            });

            function showResult(message, type) {
                result.innerHTML = message;
                result.className = `result ${type}`;
                result.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/process")
async def process_file(
    file: UploadFile = File(...),
    query_processor: QueryProcessor = Depends(get_query_processor),
    api_key: str = Depends(get_api_key)
):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    if file.size > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        contents = await file.read()
        df_queries = pd.read_excel(io.BytesIO(contents))
        
        # Process queries
        df_queries, queries_with_none_results, total_queries = await query_processor.process_queries(df_queries)
        
        # Perform calculations
        calculator = Calculator()
        df_queries = calculator.perform_calculations(df_queries)
        
        # Save results
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            df_queries.to_excel(tmp.name, index=False)
            return FileResponse(
                tmp.name,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename='processed_results.xlsx'
            )
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="Error processing file")

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/metrics")
async def metrics():
    # Implement metrics endpoint
    return {"status": "metrics endpoint"}
