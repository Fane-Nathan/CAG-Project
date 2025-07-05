# CAG System Deployment Guide

## Overview

The Cache-Augmented Generation (CAG) System consists of:
- **Backend API**: FastAPI application with GPTCache integration
- **Frontend**: Next.js web application
- **Redis Server**: Optional separate Redis management server
- **Database**: Redis for caching and history storage

## Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Node.js 18+
- Redis server
- Google Gemini API key

### Backend Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment:**
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. **Start the frontend:**
```bash
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Admin Panel: http://localhost:8000/admin

## Production Deployment

### Vercel Deployment (Recommended)

#### Backend Deployment

1. **Prepare for deployment:**
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt
```

2. **Deploy to Vercel:**
```bash
vercel --prod
```

3. **Configure environment variables in Vercel:**
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `REDIS_URL`: Your Redis connection string
- `APP_NAME`: CAG System
- `APP_VERSION`: 1.0.0

#### Frontend Deployment

1. **Build and deploy:**
```bash
cd frontend
vercel --prod
```

2. **Configure environment variables:**
- `NEXT_PUBLIC_API_URL`: Your backend API URL

### Docker Deployment

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - redis
    volumes:
      - ./gptcache_data:/app/gptcache_data

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  redis_data:
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | - | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | Yes |
| `GPTCACHE_DATA_DIR` | GPTCache data directory | `gptcache_data` | No |
| `APP_NAME` | Application name | `CAG System` | No |
| `DEBUG` | Enable debug mode | `false` | No |

### Redis Configuration

For production, consider:
- **Redis Persistence**: Enable RDB or AOF persistence
- **Memory Management**: Configure maxmemory and eviction policies
- **Security**: Use authentication and SSL/TLS
- **Clustering**: For high availability and scalability

Example Redis configuration:
```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
requirepass your_secure_password
```

## Monitoring and Maintenance

### Health Checks

- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /admin/health/detailed`
- **System Stats**: `GET /admin/stats/system`

### Admin Operations

- **Clear Cache**: `POST /admin/cache/clear`
- **Create Backup**: `POST /admin/backup/create`
- **Test Pipeline**: `POST /admin/test/cag`

### Monitoring Endpoints

Monitor these endpoints for system health:
```bash
# Basic health check
curl http://your-domain/health

# Detailed system status
curl http://your-domain/admin/health/detailed

# System statistics
curl http://your-domain/admin/stats/system
```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Run multiple backend instances
3. **Redis Clustering**: Use Redis Cluster for high availability
4. **CDN**: Use CDN for frontend static assets

### Performance Optimization

1. **Cache Configuration**: Tune GPTCache settings
2. **Redis Optimization**: Configure memory and persistence
3. **Connection Pooling**: Use Redis connection pooling
4. **Rate Limiting**: Implement API rate limiting

## Security

### Production Security Checklist

- [ ] Use HTTPS/TLS for all connections
- [ ] Secure Redis with authentication
- [ ] Rotate API keys regularly
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable CORS properly
- [ ] Monitor for suspicious activity
- [ ] Regular security updates

### API Security

```python
# Example rate limiting with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/cag")
@limiter.limit("10/minute")
async def cag_endpoint(request: Request):
    # Your endpoint logic
    pass
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check Redis server status
   - Verify connection string
   - Check network connectivity

2. **GPTCache Errors**
   - Ensure data directory exists and is writable
   - Check disk space
   - Verify Redis connectivity

3. **API Key Issues**
   - Verify Google API key is valid
   - Check API quotas and limits
   - Ensure proper permissions

4. **Frontend API Errors**
   - Check CORS configuration
   - Verify API URL configuration
   - Check network connectivity

### Logs and Debugging

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=debug
```

Check application logs:
```bash
# Docker logs
docker logs cag-backend
docker logs cag-frontend

# Vercel logs
vercel logs
```

## Support

For issues and support:
1. Check the troubleshooting section
2. Review application logs
3. Test with admin endpoints
4. Check system health endpoints