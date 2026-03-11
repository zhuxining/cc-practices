---
title: Performance
impact: MEDIUM
tags: caching, compression, etag, performance
---

# Performance

## Caching

### ETag

Support ETag for conditional requests:

```
GET /api/users/123

ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

Client can cache and validate:

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

Client validation:

```
GET /api/users/123
If-Modified-Since: Wed, 24 Jan 2025 10:00:00 GMT

→ 304 Not Modified (if unchanged)
```

### Cache-Control

```
# Public caching (cacheable by browsers and CDNs)
Cache-Control: public, max-age=3600

# Private caching (browser only)
Cache-Control: private, max-age=3600

# No caching
Cache-Control: no-cache, no-store, must-revalidate

# ETag validation
Cache-Control: no-cache              # Always validate with ETag

# Immutable resources
Cache-Control: public, max-age=31536000, immutable
```

### Cache-Control Examples

| Resource | Cache-Control |
|----------|---------------|
| Static assets | `public, max-age=31536000, immutable` |
| API data (5 min) | `public, max-age=300` |
| User-specific data | `private, max-age=60` |
| Real-time data | `no-cache` |
| Never cache | `no-store` |

### Vary Header

Specify what changes the response:

```
GET /api/users
Vary: Accept, Accept-Language, Authorization
```

---

## Compression

### Content-Encoding

Support compression for large responses:

```
GET /api/users

Accept-Encoding: gzip, br

Response:
Content-Encoding: gzip
Content-Type: application/json
```

### Compression Threshold

Compress responses larger than 1KB:

| Size | Compression |
|------|-------------|
| < 1KB | None (overhead > benefit) |
| 1KB - 10KB | gzip |
| > 10KB | gzip or brotli (br) |

### Accept-Encoding

Always respect client's Accept-Encoding header:

```
Accept-Encoding: gzip, deflate, br
```

---

## Pagination Strategies

### Offset-Based (Small Datasets)

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
  }
}
```

**Pros:** Simple to implement, supports jumping to any page
**Cons:** Performance degrades with large offsets, shows stale/missing data on changes

### Cursor-Based (Large Datasets)

For large or frequently changing datasets:

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

**Pros:** Consistent results, better performance
**Cons:** Cannot jump to specific page

### Keyset Pagination

For ordered datasets:

```
GET /api/users?limit=20&last_id=123

{
  "data": [...],
  "meta": {
    "next_id": 145
  }
}
```

---

## Response Optimization

### Field Selection

Allow clients to request specific fields:

```
GET /api/users?fields=id,name

{
  "data": [
    { "id": "1", "name": "John" }
  ]
}
```

### Sparse Fieldsets

Reduce payload size:

```
# Full response
GET /api/users/123
→ 2000 bytes

# With field selection
GET /api/users/123?fields=id,name
→ 200 bytes
```

### Compression Levels

| Level | Compression | CPU Usage |
|-------|-------------|-----------|
| 1-3 | Fast | Low |
| 4-6 | Balanced | Medium |
| 7-9 | Best | High |

Recommended: Level 4-6 for APIs

---

## HTTP/2

### Benefits

- Multiplexing (multiple requests over one connection)
- Header compression (HPACK)
- Server push (proactive resource sending)
- Binary protocol (more efficient)

### Considerations

- Requires HTTPS
- Not all clients support it
- Can change optimization strategies

---

## Performance Headers

### Timing Information

```
X-Response-Time: 145ms
X-Process-Time: 120ms
X-DB-Time: 80ms
```

### Request ID

```
X-Request-ID: unique-request-id
```

Useful for:
- Debugging
- Log aggregation
- Performance analysis

---

## Database Optimization

### Indexes

Ensure columns used in filtering, sorting, and joins are indexed:

```
# Common query
GET /api/users?status=active&sort=created_at

# Add indexes
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### Query Optimization

- Use `SELECT` with specific columns instead of `SELECT *`
- Limit result sets with pagination
- Use database-level filtering when possible

---

## CDN Usage

For static or cacheable content:

- Serve API documentation via CDN
- Cache static assets (images, stylesheets)
- Consider edge caching for public APIs

Reference: [Web Performance](https://developer.mozilla.org/docs/Web/Performance)
