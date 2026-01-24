---
title: Status Codes
impact: CRITICAL
tags: status, codes, success, errors
---

# HTTP Status Codes

## Success Codes (2xx)

| Code | Meaning | Use Case | Response Body |
|------|---------|----------|---------------|
| 200 OK | Request succeeded | GET, PUT, PATCH | Yes - return data |
| 201 Created | Resource created | POST | Yes + Location header |
| 204 No Content | Success, no body | DELETE | No |

### 200 OK

```
GET /api/users/123
→ 200 OK
{
  "id": "123",
  "name": "John",
  "email": "john@example.com"
}
```

### 201 Created

```
POST /api/users
{ "name": "John", "email": "john@example.com" }

→ 201 Created
Location: /api/users/123
{
  "id": "123",
  "name": "John",
  "email": "john@example.com"
}
```

### 204 No Content

```
DELETE /api/users/123
→ 204 No Content
```

---

## Client Error Codes (4xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 400 Bad Request | Malformed request | Invalid JSON, missing fields |
| 401 Unauthorized | Authentication required | Missing/invalid token |
| 403 Forbidden | Insufficient permissions | Authenticated but not authorized |
| 404 Not Found | Resource doesn't exist | Invalid resource ID |
| 409 Conflict | State conflict | Duplicate email, version mismatch |
| 422 Unprocessable Entity | Validation errors | Business rule violations |

### 400 Bad Request

```
POST /api/users
{ "name": "John", "email": "invalid-email" }

→ 400 Bad Request
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid request format"
  }
}
```

### 401 Unauthorized

```
GET /api/users
# No Authorization header

→ 401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

### 403 Forbidden

```
GET /api/admin/users
Authorization: Bearer regular-user-token

→ 403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Administrator access required"
  }
}
```

### 404 Not Found

```
GET /api/users/999

→ 404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User with ID 999 does not exist"
  }
}
```

### 409 Conflict

```
POST /api/users
{ "email": "existing@example.com" }

→ 409 Conflict
{
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "A user with this email already exists",
    "field": "email"
  }
}
```

### 422 Unprocessable Entity

```
POST /api/users
{ "email": "not-an-email", "age": -5 }

→ 422 Unprocessable Entity
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Invalid email format" },
      { "field": "age", "message": "Age must be positive" }
    ]
  }
}
```

---

## Server Error Codes (5xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 500 Internal Server Error | Unhandled error | Unexpected server error |
| 502 Bad Gateway | Upstream error | External service failure |
| 503 Service Unavailable | Service down | Maintenance or overload |

### 500 Internal Server Error

```
GET /api/users

→ 500 Internal Server Error
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

### 503 Service Unavailable

```
GET /api/users

→ 503 Service Unavailable
Retry-After: 3600
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service is temporarily unavailable"
  }
}
```

---

## Error Response Format

Use a consistent error response structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": [
      {
        "field": "field_name",
        "message": "Specific error message"
      }
    ],
    "timestamp": "2025-01-24T10:00:00Z",
    "path": "/api/users"
  }
}
```

Reference: [MDN HTTP Status Codes](https://developer.mozilla.org/docs/Web/HTTP/Status)
