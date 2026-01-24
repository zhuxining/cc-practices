---
title: Operations
impact: LOW
tags: health, monitoring, logging, operations
---

# Operations

## Health Endpoints

### Basic Health Check

```
GET /health

200 OK

{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-01-24T10:00:00Z"
}
```

### Detailed Health Check

```
GET /health/detailed

200 OK

{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-01-24T10:00:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 5
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1
    },
    "external_api": {
      "status": "healthy",
      "latency_ms": 50
    }
  }
}
```

### Readiness Probe

```
GET /health/ready

200 OK        # Ready to accept traffic

or

503 Service Unavailable        # Not ready
```

### Liveness Probe

```
GET /health/live

200 OK        # Application is running
```

---

## Monitoring

### Request ID

Include unique request ID for tracing:

```
GET /api/users

X-Request-ID: req_abc123xyz
```

Client can include their own ID:

```
GET /api/users
X-Request-ID: my-custom-request-id
```

Server echoes back the ID:

```
X-Request-ID: my-custom-request-id
```

### Response Time

Include timing information:

```
GET /api/users

X-Response-Time: 145ms
X-Process-Time: 120ms
X-DB-Time: 80ms
```

### Performance Metrics

```
GET /metrics

# Prometheus format
http_requests_total{method="GET",endpoint="/users"} 1234
http_request_duration_seconds{method="GET",endpoint="/users"} 0.145

# JSON format
{
  "metrics": {
    "requests_total": 1234,
    "requests_per_second": 12.5,
    "avg_response_time_ms": 145,
    "p50_response_time_ms": 120,
    "p95_response_time_ms": 200,
    "p99_response_time_ms": 350
  }
}
```

---

## Logging

### Request Logging

Log essential request information:

```
{
  "timestamp": "2025-01-24T10:00:00Z",
  "request_id": "req_abc123",
  "method": "GET",
  "path": "/api/users",
  "status": 200,
  "duration_ms": 145,
  "user_id": "123",
  "ip": "192.168.1.1"
}
```

### Error Logging

Log errors with context:

```
{
  "timestamp": "2025-01-24T10:00:00Z",
  "request_id": "req_xyz789",
  "level": "error",
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Failed to connect to database",
    "stack_trace": "...",
    "context": {
      "host": "db.example.com",
      "port": 5432
    }
  }
}
```

### Log Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed diagnostics |
| INFO | Normal operations |
| WARN | Degraded performance |
| ERROR | Errors requiring attention |
| FATAL | Critical failures |

---

## Deployment

### Blue-Green Deployment

Maintain two production environments:

```
# Blue (current)
https://api-blue.example.com

# Green (new version)
https://api-green.example.com

# Switch traffic by updating DNS or load balancer
https://api.example.com → api-green.example.com
```

### Canary Deployment

Roll out to subset of users:

```
# 90% → old version
# 10% → new version (canary)
```

Monitor canary for issues before full rollout.

### Feature Flags

Enable/disable features without deployment:

```
GET /api/users
X-Feature-Flags: new_pagination,v2_responses

Response uses new features based on flags
```

---

## Maintenance Mode

### Maintenance Response

```
GET /api/users

503 Service Unavailable
Retry-After: 3600

{
  "error": {
    "code": "MAINTENANCE_MODE",
    "message": "API is under maintenance. Will be back in 1 hour.",
    "estimated_restoration": "2025-01-24T11:00:00Z"
  }
}
```

### Scheduled Maintenance Header

Warn about upcoming maintenance:

```
GET /api/users

X-Maintenance-Window: 2025-01-25T02:00:00Z/2025-01-25T04:00:00Z
```

---

## Webhooks

### Webhook Signature

Sign webhook payloads for security:

```
X-Webhook-Signature: sha256=signature_here
X-Webhook-Timestamp: 1737715200
```

Verify signature:

```
signature = HMAC-SHA256(webhook_secret, payload)
```

### Webhook Retry

Implement retry logic for failed webhooks:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 1 hour |

Give up after N attempts (e.g., 5).

---

## Configuration

### Environment-Based Configuration

```
# Development
https://api-dev.example.com

# Staging
https://api-staging.example.com

# Production
https://api.example.com
```

### Configuration Endpoint

```
GET /api/config

{
  "version": "2.0.0",
  "features": {
    "new_pagination": true,
    "bulk_operations": true
  },
  "limits": {
    "max_page_size": 100,
    "max_batch_size": 50
  }
}
```

---

## Incident Response

### Error Tracking

Integrate with error tracking service:

```
# Sentry, Rollbar, etc.
{
  "error_id": "err_abc123",
  "request_id": "req_xyz789"
}
```

Include error ID in responses:

```
500 Internal Server Error

{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "error_id": "err_abc123"
  }
}
```

### Status Page

Provide public status page:

```
https://status.example.com

All Systems Operational
  ✓ API
  ✓ Database
  ✓ CDN
```

Reference: [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
