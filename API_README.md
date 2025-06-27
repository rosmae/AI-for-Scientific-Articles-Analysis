# Prime Time Medical Research Opportunities API

This is the FastAPI version of the Prime Time Medical Research Opportunities application. It provides a REST API for analyzing medical research opportunities using PubMed data.

## Features

- **Keyword Generation**: Generate relevant keywords from research ideas using BERT
- **PubMed Search**: Search PubMed with MeSH term expansion
- **Article Management**: Store and retrieve articles with metadata
- **Opportunity Scoring**: Compute novelty, citation velocity, and recency scores
- **Data Export**: Export articles to CSV format
- **Background Processing**: Clustering and forecasting analysis

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root with your database configuration:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=prime_time_db
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
```

### 3. Database Setup

Make sure your PostgreSQL database is running and accessible with the credentials in your `.env` file.

## Running the API

### Development Mode

```bash
cd src
python main_api.py
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
cd src
uvicorn main_api:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Main Endpoints

### Health Check
- `GET /health` - Check API status

### Database Management
- `POST /database/connect` - Connect to database with custom config
- `POST /database/initialize` - Initialize database schema

### Keyword Generation
- `POST /keywords/generate` - Generate keywords from research idea

### PubMed Search
- `POST /search/pubmed` - Search PubMed and store articles

### Articles
- `GET /articles` - Get all articles
- `GET /articles/{pmid}` - Get specific article details

### Opportunity Scores
- `GET /search/{search_id}/scores` - Get opportunity scores for a search

### Data Export
- `GET /export/csv` - Export all articles to CSV

### Search History
- `GET /searches` - Get search history

## Example Usage

### 1. Generate Keywords

```bash
curl -X POST "http://localhost:8000/keywords/generate" \
     -H "Content-Type: application/json" \
     -d '{"idea": "machine learning applications in cancer diagnosis"}'
```

### 2. Search PubMed

```bash
curl -X POST "http://localhost:8000/search/pubmed" \
     -H "Content-Type: application/json" \
     -d '{
       "keywords": "machine learning; cancer diagnosis",
       "idea_text": "machine learning applications in cancer diagnosis",
       "max_results": 20
     }'
```

### 3. Get Articles

```bash
curl "http://localhost:8000/articles"
```

## Architecture

The API follows a clean architecture pattern:

- **Models**: Pydantic models for request/response validation
- **Services**: Core business logic (database, ML models)
- **Endpoints**: FastAPI route handlers
- **Background Tasks**: Async processing for heavy operations

## Background Processing

The API uses FastAPI's background tasks for:
- Clustering analysis
- Forecasting pipeline
- Opportunity score computation

These operations run asynchronously to avoid blocking the API response.

## Error Handling

The API includes comprehensive error handling:
- HTTP status codes for different error types
- Detailed error messages
- Input validation using Pydantic
- Database connection error handling

## CORS Configuration

The API includes CORS middleware configured to allow all origins. For production, you should configure this properly:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Performance Considerations

- ML models are loaded once at startup and reused
- Database connections are managed efficiently
- Background tasks for heavy operations
- Optional: Use `ujson` or `orjson` for faster JSON processing

## Development

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Create the endpoint function with proper error handling
3. Add to the FastAPI app
4. Update documentation

### Testing

You can test the API using:
- The interactive docs at `/docs`
- curl commands
- Postman or similar tools
- Automated tests (to be implemented)

## Deployment

### Docker (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["uvicorn", "src.main_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

The API can be deployed to:
- Heroku
- AWS Lambda + API Gateway
- Google Cloud Run
- Azure App Service
- DigitalOcean App Platform

## Monitoring

Consider adding:
- Logging (structured logging with JSON)
- Metrics (Prometheus/Grafana)
- Health checks
- Error tracking (Sentry)

## Security

For production:
- Use HTTPS
- Implement authentication/authorization
- Rate limiting
- Input sanitization
- Secure database connections 