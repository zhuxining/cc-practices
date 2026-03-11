---
title: Response Format
impact: HIGH
tags: response, format, error, pagination
---

# Response Format

## Response Structure

### Single Resource Response

```
GET /api/users/123

{
  "data": {
    "id": "123",
    "name": "John",
    "email": "john@example.com"
  }
}
```

### Collection Response

```
GET /api/users?page=1&per_page=20

{
  "data": [
    { "id": "1", "name": "John" },
    { "id": "2", "name": "Jane" }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/users?page=1",
    "next": "/users?page=2",
    "prev": null,
    "first": "/users?page=1",
    "last": "/users?page=8"
  }
}
```

### Naming Conventions

Use `snake_case` for JSON keys:

```json
{
  "user_id": "123",
  "first_name": "John",
  "created_at": "2025-01-24T10:00:00Z"
}
```

---

## Error Responses

### Consistent Error Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "timestamp": "2025-01-24T10:00:00Z",
    "path": "/api/users"
  }
}
```

### Validation Error Example

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Invalid email format" },
      { "field": "age", "message": "Age must be positive" },
      { "field": "password", "message": "Password must be at least 8 characters" }
    ]
  }
}
```

### Standard Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `UNAUTHORIZED` | Authentication required |
| `FORBIDDEN` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource state conflict |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## Pagination

### Offset-Based Pagination

For small, stable datasets:

```
GET /api/users?page=2&per_page=20

{
  "data": [...],
  "meta": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/users?page=2&per_page=20",
    "next": "/users?page=3&per_page=20",
    "prev": "/users?page=1&per_page=20",
    "first": "/users?page=1&per_page=20",
    "last": "/users?page=8&per_page=20"
  }
}
```

### Cursor-Based Pagination

For large or real-time datasets:

```
GET /api/users?limit=20&cursor=eyJpZCI6MTIzfQ

{
  "data": [...],
  "meta": {
    "limit": 20,
    "has_more": true
  },
  "links": {
    "next": "/users?limit=20&cursor=eyJpZCI6MTQzfQ"
  }
}
```

### Link Header Pagination

Use HTTP headers for pagination info:

```
GET /api/users?page=2

Link: <https://api.example.com/users?page=3>; rel="next",
      <https://api.example.com/users?page=1>; rel="prev",
      <https://api.example.com/users?page=1>; rel="first",
      <https://api.example.com/users?page=8>; rel="last"
```

---

## Conditional Requests

### ETag

Support conditional requests with ETag:

```
GET /api/users/123

ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

Client can use If-None-Match:

```
GET /api/users/123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

→ 304 Not Modified (if unchanged)
```

### Last-Modified

```
GET /api/users/123

Last-Modified: Wed, 24 Jan 2025 10:00:00 GMT
```

Client can use If-Modified-Since:

```
GET /api/users/123
If-Modified-Since: Wed, 24 Jan 2025 10:00:00 GMT

→ 304 Not Modified (if unchanged)
```

---

## Common Response Headers

### Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1640000000
```

### Request ID

```
X-Request-ID: unique-request-id
```

### Response Time

```
X-Response-Time: 145ms
```

---

## Sparse Fieldsets

Allow clients to request specific fields:

```
GET /api/users?fields=id,name,email

{
  "data": [
    { "id": "1", "name": "John", "email": "john@example.com" }
  ]
}
```

Use dot notation for nested fields:

```
GET /api/users?fields=id,name,avatar.url
```
