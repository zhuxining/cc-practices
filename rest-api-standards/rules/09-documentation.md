---
title: Documentation
impact: LOW
tags: openapi, documentation, api-docs
---

# Documentation

## OpenAPI Specification

### OpenAPI 3.0+

Use OpenAPI 3.0+ for API specification:

```yaml
openapi: 3.2.0
info:
  title: My API
  version: 2.0.0
  description: API for managing users
  contact:
    name: API Support
    email: support@example.com

servers:
  - url: https://api.example.com/v2
    description: Production server

paths:
  /users:
    get:
      summary: List all users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: per_page
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'

    post:
      summary: Create a new user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          headers:
            Location:
              description: URL of the new user
              schema:
                type: string

  /users/{userId}:
    get:
      summary: Get user by ID
      operationId: getUser
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
          format: email

    UserCreate:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email
```

---

## Documentation Best Practices

### Complete Coverage

Document all endpoints:

- All HTTP methods
- All parameters
- All request body schemas
- All response codes
- All response schemas

### Examples

Include request/response examples:

```yaml
responses:
  '200':
    description: Successful response
    content:
      application/json:
        examples:
          success:
            summary: Successful response example
            value:
              data:
                - id: "1"
                  name: "John"
                  email: "john@example.com"
```

### Error Documentation

Document all possible errors:

```yaml
responses:
  '400':
    description: Bad request
    content:
      application/json:
        example:
          error:
            code: "VALIDATION_ERROR"
            message: "Request validation failed"
  '401':
    description: Unauthorized
  '404':
    description: User not found
```

---

## API Documentation Pages

### Getting Started Guide

Provide quick start documentation:

```
# Quick Start

## 1. Get API Key

Sign up at https://example.com/signup to get your API key.

## 2. Make Your First Request

curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.example.com/v2/users

## 3. Response

{
  "data": [
    { "id": "1", "name": "John", "email": "john@example.com" }
  ]
}
```

### Authentication Documentation

```
# Authentication

## Bearer Token

Include your API key in the Authorization header:

Authorization: Bearer YOUR_API_KEY

## Getting a Token

POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "refresh_token_here",
  "expires_in": 3600
}
```

### Rate Limiting Documentation

```
# Rate Limiting

- 1000 requests per hour
- 100 requests per minute

Headers returned:
- X-RateLimit-Limit: 1000
- X-RateLimit-Remaining: 742
- X-RateLimit-Reset: 1737715200
```

---

## Interactive Documentation

### Swagger UI

Provide interactive API explorer:

```
https://api.example.com/docs
```

Features:

- Try out endpoints
- See request/response formats
- Test authentication
- View all available endpoints

### ReDoc

Alternative documentation view:

```
https://api.example.com/redoc
```

Features:

- Clean, readable layout
- Three-panel design
- Code samples
- Search functionality

---

## Changelog

Maintain a changelog:

```
# Changelog

## [2.0.0] - 2025-01-24

### Added
- Field selection with `fields` parameter
- Cursor-based pagination
- Rate limiting headers

### Changed
- Renamed `user_name` to `name` (breaking change)
- Updated authentication to use JWT

### Deprecated
- `/api/v1/users` - Use `/api/v2/users` instead

### Removed
- XML response format

### Fixed
- Pagination overflow issue
- CORS configuration
```

---

## Code Samples

Provide samples in multiple languages:

```
# Create User

## curl

curl -X POST https://api.example.com/v2/users \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'

## JavaScript

fetch('https://api.example.com/v2/users', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'John',
    email: 'john@example.com'
  })
})

## Python

import requests

response = requests.post(
  'https://api.example.com/v2/users',
  headers={
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  json={
    'name': 'John',
    'email': 'john@example.com'
  })
```

---

## SDKs and Client Libraries

Consider providing official SDKs:

- JavaScript/TypeScript
- Python
- Java
- Go
- PHP

Reference: [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
