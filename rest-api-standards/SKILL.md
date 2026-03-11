---
name: rest-api-standards
description: Framework-agnostic REST API design standards and specifications. Use when designing REST APIs, reviewing API structures, implementing endpoints, or making decisions about HTTP methods, URI design, status codes, authentication, pagination, or versioning. Covers 10 categories with comprehensive guidelines.
version: 1.0.0
---

# REST API Standards

Comprehensive framework-agnostic standards for designing RESTful APIs following industry conventions. Contains guidelines across 10 categories, organized by priority to guide API design, implementation, and review.

## When to Apply

Reference these standards when:

- Designing new REST API endpoints
- Refactoring existing API structures
- Reviewing API designs for consistency
- Implementing authentication/authorization
- Adding pagination or filtering
- Planning API versioning strategy
- Implementing rate limiting or caching
- Documenting APIs with OpenAPI

## Philosophy

This guide is **framework-agnostic** and applies to any programming language or framework. Examples use generic HTTP notation that translates to any technology stack.

## Standard Categories by Priority

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Core Basics | CRITICAL |
| 1 | Status Codes | CRITICAL |
| 2 | Request Format | HIGH |
| 2 | Response Format | HIGH |
| 2 | Security | HIGH |
| 3 | Advanced Operations | MEDIUM |
| 3 | API Versioning | MEDIUM |
| 3 | Performance | MEDIUM |
| 4 | Documentation | LOW |
| 4 | Operations | LOW |

## Quick Reference

### Core Basics (CRITICAL)

- Use nouns for resources, not verbs
- Map HTTP methods correctly (GET/POST/PUT/PATCH/DELETE)
- Use kebab-case for multi-word resources
- Use plural nouns for collections
- Limit nesting to 3-4 levels
- Use query parameters for filtering

### Status Codes (CRITICAL)

- 200 OK - Standard success
- 201 Created - Resource created (+ Location header)
- 204 No Content - Success with no body
- 400, 401, 403, 404, 409, 422 - Client errors
- 500, 502, 503 - Server errors

### Request Format (HIGH)

- Use snake_case for query parameters
- Support filtering (?status=active)
- Support sorting (?sort=name, ?sort=-created_at)
- Support searching (?search=john)

### Response Format (HIGH)

- Consistent response structure
- Standard error format with code/message/details
- Pagination with meta/links
- Support ETag for caching

### Security (HIGH)

- Bearer token authentication
- Rate limiting headers
- Proper CORS configuration
- HTTPS only

### Advanced Operations (MEDIUM)

- Bulk operations endpoints
- Idempotency keys for POST
- PATCH for partial updates

### API Versioning (MEDIUM)

- URL versioning (/api/v1/users)
- Version only for breaking changes
- Maintain old versions 6-12 months

### Performance (MEDIUM)

- ETag and Cache-Control headers
- Compression (gzip/br)
- Cursor-based pagination for large datasets

### Documentation (LOW)

- OpenAPI 3.0+ specification
- Interactive documentation (Swagger UI)
- Code samples in multiple languages

### Operations (LOW)

- Health check endpoints (/health)
- Request ID for tracing
- Response time headers
- Error tracking

## How to Use

Consult individual standard files in [rules/](rules/):

```
rules/01-core-basics.md       # HTTP Methods & URI Design
rules/02-status-codes.md      # Status Codes
rules/03-request-format.md    # Query Parameters & Filtering
rules/04-response-format.md   # Response Structure & Pagination
rules/05-advanced-operations.md  # Bulk Operations & Idempotency
rules/06-api-versioning.md    # Versioning Strategies
rules/07-security.md          # Authentication & Rate Limiting
rules/08-performance.md       # Caching & Compression
rules/09-documentation.md     # OpenAPI & Docs
rules/10-operations.md        # Health & Monitoring
```

## External References

- [MDN HTTP Documentation](https://developer.mozilla.org/docs/Web/HTTP)
- [RFC 9110: HTTP Semantics](https://httpwg.org/specs/rfc9110.html)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [REST API Tutorial](https://restfulapi.net/)
