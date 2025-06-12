
## Features

- Excel file upload and processing
- SQL query execution from Excel cells
- Automated calculations based on query results
- Async database operations
- Connection pooling
- API key authentication
- Rate limiting
- Comprehensive error handling
- Structured logging
- Monitoring and metrics
- Docker support
- Test suite

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis (optional, for caching)
- Docker and Docker Compose (for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd query-processor-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lfuportal

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false

# Security
API_KEY=your_api_key
ALLOWED_HOSTS=["*"]
CORS_ORIGINS=["*"]
MAX_FILE_SIZE=10485760  # 10MB

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_ENABLED=true
TRACING_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
docker-compose up --build
```

## API Endpoints

### Upload and Process Excel File
- **URL**: `/process`
- **Method**: `POST`
- **Headers**: 
  - `X-API-Key`: Your API key
- **Body**: 
  - `file`: Excel file (.xlsx)
- **Response**: Processed Excel file

### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**: API health status

### Metrics
- **URL**: `/metrics`
- **Method**: `GET`
- **Response**: Application metrics

## Database Schema

The application expects a PostgreSQL database with the following configuration:
- Database name: `lfuportal`
- User: `postgres` (configurable)
- Port: `5432` (configurable)

## Testing

Run the test suite:
```bash
pytest
```

## Monitoring

The application includes:
- Prometheus metrics
- Sentry error tracking
- OpenTelemetry tracing
- Structured logging

## Security Features

- API key authentication
- CORS configuration
- Rate limiting
- Input validation
- Secure file handling
- Environment variable management

## Performance Optimizations

- Async database operations
- Connection pooling
- Redis caching (optional)
- Efficient file processing
- Optimized calculations

## Error Handling

The application implements comprehensive error handling for:
- Database connection issues
- Invalid file formats
- SQL query errors
- Calculation errors
- Authentication failures
- Rate limiting
- File size limits

## Logging

Logs are written to:
- Console (development)
- File (production)
- Sentry (if configured)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License]

## Support

For support, please [contact information]