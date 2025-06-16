# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
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
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #4a5a6a 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                color: #ecf0f1;
            }

            .container {
                background: #34495e;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                overflow: hidden;
                width: 100%;
                max-width: 600px;
                backdrop-filter: blur(10px);
                border: 1px solid #4a5a6a;
            }

            .header {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                padding: 40px 20px;
                text-align: center;
                color: white;
            }

            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 10px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }

            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }

            .port-instruction {
                background: #e74c3c;
                color: white;
                padding: 15px 20px;
                text-align: center;
                font-size: 0.95rem;
                border-bottom: 1px solid #c0392b;
            }

            .port-instruction strong {
                display: block;
                margin-bottom: 5px;
                font-size: 1.05rem;
            }

            .port-instruction span {
                background: rgba(255,255,255,0.2);
                padding: 2px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }

            .content {
                padding: 40px;
                background: #34495e;
            }

            .upload-section {
                margin-bottom: 30px;
            }

            .upload-form {
                border: 3px dashed #5a6c7d;
                border-radius: 15px;
                padding: 40px 20px;
                text-align: center;
                transition: all 0.3s ease;
                background: #3a4a5c;
                position: relative;
                overflow: hidden;
            }

            .upload-form::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transition: left 0.5s;
            }

            .upload-form:hover {
                border-color: #3498db;
                background: #3e526b;
                transform: translateY(-2px);
            }

            .upload-form:hover::before {
                left: 100%;
            }

            .upload-icon {
                font-size: 3rem;
                color: #3498db;
                margin-bottom: 20px;
            }

            .upload-text {
                font-size: 1.2rem;
                color: #bdc3c7;
                margin-bottom: 20px;
            }

            .upload-text strong {
                color: #ecf0f1;
            }

            .file-input-wrapper {
                position: relative;
                display: inline-block;
                margin: 20px 0;
            }

            .file-input {
                position: absolute;
                opacity: 0;
                width: 100%;
                height: 100%;
                cursor: pointer;
            }

            .file-input-button {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-block;
                box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            }

            .file-input-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
            }

            .file-name {
                margin-top: 15px;
                font-size: 0.9rem;
                color: #95a5a6;
                font-style: italic;
            }

            .options-section {
                margin: 30px 0;
                padding: 25px;
                background: #3a4a5c;
                border-radius: 15px;
                border: 1px solid #4a5a6a;
            }

            .options-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: #ecf0f1;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .calculation-toggle {
                display: flex;
                align-items: center;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }

            .toggle-label {
                font-size: 1rem;
                color: #bdc3c7;
                font-weight: 500;
            }

            .dropdown-wrapper {
                position: relative;
            }

            .calculation-dropdown {
                background: #2c3e50;
                border: 2px solid #4a5a6a;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 1rem;
                color: #ecf0f1;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 200px;
                appearance: none;
                background-image: url('data:image/svg+xml;utf8,<svg fill="%23ecf0f1" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M7 10l5 5 5-5z"/><path d="M0 0h24v24H0z" fill="none"/></svg>');
                background-repeat: no-repeat;
                background-position: right 10px center;
                background-size: 20px;
                padding-right: 40px;
            }

            .calculation-dropdown:focus {
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
            }

            .calculation-dropdown:hover {
                border-color: #3498db;
            }

            .calculation-dropdown option {
                background: #2c3e50;
                color: #ecf0f1;
            }

            .calculation-instruction {
                margin-bottom: 20px;
                padding: 15px;
                background: #2c4a3d;
                border-radius: 10px;
                border-left: 4px solid #27ae60;
                font-size: 0.95rem;
            }

            .instruction-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
                color: #a8e6cf;
                font-size: 1rem;
            }

            .instruction-content {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .instruction-item {
                display: flex;
                align-items: center;
                gap: 10px;
                color: #d5f4e6;
                font-size: 0.9rem;
            }

            .bullet {
                font-size: 1rem;
                font-weight: bold;
                min-width: 20px;
            }

            .calculation-info {
                margin-top: 10px;
                padding: 10px;
                background: #2c5282;
                border-radius: 8px;
                font-size: 0.9rem;
                color: #bee3f8;
                border-left: 4px solid #3498db;
            }

            .submit-btn {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            }

            .submit-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
            }

            .submit-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }

            .download-btn {
                background: linear-gradient(135deg, #27ae60 0%, #219a52 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
            }

            .download-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4);
            }

            .status-message {
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                font-weight: 500;
                display: none;
            }

            .status-success {
                background: #27ae60;
                color: white;
                border: 1px solid #219a52;
            }

            .status-error {
                background: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
            }

            .processing {
                display: none;
                text-align: center;
                margin: 20px 0;
            }

            .spinner {
                border: 3px solid #4a5a6a;
                border-top: 3px solid #3498db;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }

            .feature {
                text-align: center;
                padding: 20px;
                background: #3a4a5c;
                border-radius: 10px;
                transition: transform 0.3s ease;
                border: 1px solid #4a5a6a;
            }

            .feature:hover {
                transform: translateY(-5px);
            }

            .feature-icon {
                font-size: 2rem;
                margin-bottom: 10px;
            }

            .feature h4 {
                color: #ecf0f1;
                margin-bottom: 5px;
            }

            .feature p {
                color: #bdc3c7;
                font-size: 0.9rem;
            }

            .download-section {
                border-top: 1px solid #4a5a6a;
                padding-top: 30px;
                text-align: center;
            }

            .download-section h3 {
                color: #ecf0f1;
                margin-bottom: 10px;
            }

            .download-section p {
                color: #bdc3c7;
                margin-bottom: 20px;
            }

            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .content {
                    padding: 20px;
                }
                
                .features {
                    grid-template-columns: 1fr;
                }

                .calculation-toggle {
                    flex-direction: column;
                    align-items: stretch;
                }

                .calculation-dropdown {
                    min-width: 100%;
                }

                .calculation-instruction {
                    margin-bottom: 15px;
                    padding: 12px;
                    font-size: 0.85rem;
                }

                .instruction-content {
                    gap: 6px;
                }

                .instruction-item {
                    font-size: 0.85rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PATO Tracker Query Processor</h1>
                <p>Get the PATO KPI numbers by just Uploading the query file</p>
            </div>
            
            <div class="port-instruction">
                <strong>⚠️ Important Setup Instructions:</strong>
                Please change the port number in your <span>.env</span> file. You can get the correct port number from the GCP command shared with you.
            </div>
            
            <div class="content">
                <div class="upload-section">
                    <form id="uploadForm" action="/process" method="post" enctype="multipart/form-data">
                        <div class="upload-form">
                            <div class="upload-icon">📊</div>
                            <div class="upload-text">
                                <strong>Upload your CSV file</strong><br>
                                Drag and drop or click to browse
                            </div>
                            <div class="file-input-wrapper">
                                <input type="file" name="file" id="fileInput" accept=".csv" class="file-input" required>
                                <label for="fileInput" class="file-input-button">Choose File</label>
                            </div>
                            <div id="fileName" class="file-name"></div>
                        </div>

                        <div class="options-section">
                            <div class="options-title">
                                <span>⚙️</span>
                                <span>Processing Options</span>
                            </div>
                            
                            <div class="calculation-instruction">
                                <div class="instruction-header">
                                    <span>📋</span>
                                    <strong>Important Calculation Guidelines:</strong>
                                </div>
                                <div class="instruction-content">
                                    <div class="instruction-item">
                                        <span class="bullet">✅</span>
                                        <span><strong>Main Sheet:</strong> Enable calculations</span>
                                    </div>
                                    <div class="instruction-item">
                                        <span class="bullet">❌</span>
                                        <span><strong>All Other Sheets:</strong> Disable calculations</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="calculation-toggle">
                                <label class="toggle-label" for="performCalculations">Enable Calculations:</label>
                                <div class="dropdown-wrapper">
                                    <select name="perform_calculations" id="performCalculations" class="calculation-dropdown">
                                        <option value="true">Yes - Perform calculations</option>
                                        <option value="false">No - Skip calculations</option>
                                    </select>
                                </div>
                            </div>
                            <div class="calculation-info" id="calculationInfo">
                                <strong>📊 Calculations Enabled:</strong> Mathematical operations and formulas will be processed automatically.
                            </div>
                        </div>
                        
                        <div class="processing" id="processing">
                            <div class="spinner"></div>
                            <p>Processing your file...</p>
                        </div>
                        
                        <div class="status-message" id="statusMessage"></div>
                        
                        <button type="submit" class="submit-btn" id="submitBtn">
                            🚀 Process File
                        </button>
                    </form>
                </div>

                <div class="download-section" id="downloadSection" style="display: none;">
                    <div>
                        <h3>📥 Download Results</h3>
                        <p>Your file has been processed successfully!</p>
                        <button class="download-btn" id="downloadBtn">
                            ⬇️ Download Processed CSV
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const fileName = document.getElementById('fileName');
            const uploadForm = document.getElementById('uploadForm');
            const submitBtn = document.getElementById('submitBtn');
            const processing = document.getElementById('processing');
            const statusMessage = document.getElementById('statusMessage');
            const performCalculations = document.getElementById('performCalculations');
            const calculationInfo = document.getElementById('calculationInfo');
            const downloadSection = document.getElementById('downloadSection');
            const downloadBtn = document.getElementById('downloadBtn');
            
            let processedFileBlob = null;
            let processedFileName = 'processed_results.csv';

            // File input change handler
            fileInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    fileName.textContent = `Selected: ${e.target.files[0].name}`;
                    fileName.style.color = '#3498db';
                } else {
                    fileName.textContent = '';
                }
            });

            // Calculation toggle handler
            performCalculations.addEventListener('change', function(e) {
                const isEnabled = e.target.value === 'true';
                if (isEnabled) {
                    calculationInfo.innerHTML = '<strong>📊 Calculations Enabled:</strong> Mathematical operations and formulas will be processed automatically.';
                    calculationInfo.style.background = '#2c5282';
                    calculationInfo.style.borderLeftColor = '#3498db';
                    calculationInfo.style.color = '#bee3f8';
                } else {
                    calculationInfo.innerHTML = '<strong>⏭️ Calculations Disabled:</strong> Only query processing will be performed, mathematical operations will be skipped.';
                    calculationInfo.style.background = '#b7791f';
                    calculationInfo.style.borderLeftColor = '#f39c12';
                    calculationInfo.style.color = '#fef5e7';
                }
            });

            // Drag and drop functionality
            const uploadFormArea = document.querySelector('.upload-form');
            
            uploadFormArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.style.borderColor = '#3498db';
                this.style.background = '#3e526b';
            });

            uploadFormArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.style.borderColor = '#5a6c7d';
                this.style.background = '#3a4a5c';
            });

            uploadFormArea.addEventListener('drop', function(e) {
                e.preventDefault();
                this.style.borderColor = '#5a6c7d';
                this.style.background = '#3a4a5c';
                
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type === 'text/csv') {
                    fileInput.files = files;
                    fileName.textContent = `Selected: ${files[0].name}`;
                    fileName.style.color = '#3498db';
                }
            });

            // Form submission handler
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault(); // Always prevent default form submission
                
                if (!fileInput.files.length) {
                    showStatus('Please select a CSV file first.', 'error');
                    return;
                }

                // Show processing state
                submitBtn.disabled = true;
                processing.style.display = 'block';
                statusMessage.style.display = 'none';

                // Create FormData and submit via fetch
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('perform_calculations', performCalculations.value);

                fetch('/process', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        // Get the filename from the response headers
                        const contentDisposition = response.headers.get('Content-Disposition');
                        let filename = 'processed_results.csv';
                        if (contentDisposition) {
                            const filenameMatch = contentDisposition.match(/filename=(.+)/);
                            if (filenameMatch) {
                                filename = filenameMatch[1].replace(/"/g, '');
                            }
                        }
                        
                        // Store the blob and filename for later download
                        return response.blob().then(blob => {
                            processedFileBlob = blob;
                            processedFileName = filename;
                            
                            // Show download section
                            downloadSection.style.display = 'block';
                            downloadSection.scrollIntoView({ behavior: 'smooth' });
                            
                            showStatus('File processed successfully! Click the download button below.', 'success');
                        });
                    } else {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showStatus('Error processing file. Please try again.', 'error');
                })
                .finally(() => {
                    // Reset form state
                    submitBtn.disabled = false;
                    processing.style.display = 'none';
                });
            });

            // Download button handler
            downloadBtn.addEventListener('click', function() {
                if (processedFileBlob) {
                    const url = window.URL.createObjectURL(processedFileBlob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = processedFileName;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    showStatus('File downloaded successfully!', 'success');
                } else {
                    showStatus('No file available for download. Please process a file first.', 'error');
                }
            });

            function showStatus(message, type) {
                statusMessage.textContent = message;
                statusMessage.className = `status-message status-${type}`;
                statusMessage.style.display = 'block';
                
                // Auto-hide success messages after 5 seconds
                if (type === 'success') {
                    setTimeout(() => {
                        statusMessage.style.display = 'none';
                    }, 5000);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@router.post("/process")
async def process_file(
    file: UploadFile = File(...),
    perform_calculations: bool = Form(True),
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
        
        # Perform calculations only if enabled
        if perform_calculations:
            logger.info("Performing calculations on processed data")
            calculator = Calculator()
            df_queries = calculator.perform_calculations(df_queries)
        else:
            logger.info("Skipping calculations as requested")
        
        # Save results as CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8') as tmp:
            df_queries.to_csv(
                tmp.name,
                index=False,
                encoding='utf-8'
            )
            
            # Generate filename based on processing options
            filename_suffix = "_with_calculations" if perform_calculations else "_queries_only"
            output_filename = f'processed_results{filename_suffix}.csv'
            
            return FileResponse(
                tmp.name,
                media_type='text/csv',
                filename=output_filename,
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/check-processed-file")
async def check_processed_file():
    """Check if a processed file is available for download"""
    # This is a placeholder - you might want to implement actual file checking logic
    # based on your application's requirements
    return JSONResponse({"available": False})

@router.get("/download")
async def download_processed_file():
    """Download the most recently processed file"""
    # This is a placeholder - you'll need to implement the actual download logic
    # based on how you want to store and retrieve processed files
    raise HTTPException(status_code=404, detail="No processed file available for download")