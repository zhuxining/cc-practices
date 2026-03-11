---
title: Security
impact: HIGH
tags: authentication, authorization, rate-limiting, cors
---

# Security

## Authentication

### Bearer Token

Use the Authorization header with Bearer token:

```
GET /api/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (no token):
401 Unauthorized

{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

### Token Format

Use JWT or opaque tokens:

```
# JWT format
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Opaque token
Authorization: Bearer tok_abc123xyz
```

### Token Refresh

Provide refresh mechanism:

```
POST /api/auth/refresh
{
  "refresh_token": "refresh_token_here"
}

{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "expires_in": 3600
}
```

---

## Authorization

### OAuth2 Scopes

Use scopes for permission granularity:

```
Authorization: Bearer <token_with_scopes>

# Token with scopes: "read:users write:users"
```

Check scopes before allowing access:

```
GET /api/users          # Requires "read:users"
POST /api/users         # Requires "write:users"
DELETE /api/users/123   # Requires "delete:users"
```

### Permission Headers

Return user permissions in response headers:

```
GET /api/users/123
X-User-Permissions: read:users,write:orders
X-User-Scopes: read:users write:users
```

### Insufficient Permissions

```
DELETE /api/users/123
Authorization: Bearer read_only_token

403 Forbidden

{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Delete permission required",
    "required_scope": "delete:users"
  }
}
```

---

## Rate Limiting

### Rate Limit Headers

Include rate limit info in responses:

```
GET /api/users

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1737715200
X-RateLimit-Reset-After: 3600
```

### Rate Limit Exceeded

```
GET /api/users
# Exceeded rate limit

429 Too Many Requests
Retry-After: 3600
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1737715200

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

### Rate Limit Strategies

| Strategy | Description |
|----------|-------------|
| Per IP | Limit by client IP address |
| Per User | Limit by authenticated user |
| Per API Key | Limit by API key |
| Sliding Window | More accurate, memory intensive |
| Token Bucket | Bursts allowed, steady rate |

---

## API Keys

### API Key Header

```
GET /api/users
X-API-Key: your-api-key-here
```

### API Key in Query (Less Secure)

```
GET /api/users?api_key=your-api-key-here
```

**Note:** Prefer header over query parameter for security.

---

## CORS

### CORS Headers

```
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

### Preflight Request

```
OPTIONS /api/users

Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

### Expose Headers

Expose custom headers to client:

```
Access-Control-Expose-Headers: X-Request-ID, X-RateLimit-Remaining
```

---

## Security Headers

### Standard Security Headers

```
# Prevent clickjacking
X-Frame-Options: DENY

# Prevent MIME type sniffing
X-Content-Type-Options: nosniff

# Enable XSS filter
X-XSS-Protection: 1; mode=block

# Content Security Policy
Content-Security-Policy: default-src 'self'

# Strict Transport Security (HTTPS only)
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## HTTPS Only

Always use HTTPS for API endpoints:

```
# Redirect HTTP to HTTPS
http://api.example.com/users
→ 301 Moved Permanently
→ https://api.example.com/users

# Reject HTTP directly
http://api.example.com/users
→ 403 Forbidden
{
  "error": {
    "code": "HTTPS_REQUIRED",
    "message": "HTTPS is required for all API requests"
  }
}
```

---

## Input Validation

### Validate All Input

- Type checking
- Length limits
- Allowed values
- Format validation

### Sanitize Output

Never expose sensitive information in error messages:

```
# Bad
Internal Server Error: Database connection failed to db.example.com

# Good
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

---

## Request Signing

For high-security APIs, sign requests:

```
POST /api/users
X-API-Key: public_key
X-Signature: computed_signature
X-Timestamp: 1737715200
```

Signature = HMAC-SHA256(API_Secret, Timestamp + Method + Path + Body)

Reference: [OWASP API Security](https://owasp.org/www-project-api-security/)
