---
title: Request Format
impact: HIGH
tags: request, headers, query, filtering, sorting
---

# Request Format

## Query Parameters

### Naming Conventions

Use `snake_case` for query parameters:

```
GET /api/users?status=active
GET /api/users?created_after=2025-01-01
GET /api/orders?page=2&per_page=20
```

### Boolean Values

Use boolean values, not string representations:

```
GET /api/users?active=true
GET /api/users?include_deleted=false
```

### Array Parameters

Use comma-separated values for arrays:

```
GET /api/products?tags=red,green,blue
GET /api/users?roles=admin,moderator,user
```

---

## Filtering

### Basic Filtering

```
GET /api/users?status=active
GET /api/users?role=admin
GET /api/orders?status=pending
```

### Multiple Filters

Combine filters with `&` (AND logic):

```
GET /api/users?status=active&role=admin
GET /api/products?category=electronics&brand=apple&in_stock=true
```

### Comparison Operators

Use standard operators for comparisons:

| Operator | Syntax | Example |
|----------|--------|---------|
| Equals | `field=value` | `?status=active` |
| Not equals | `field!=value` | `?status!=deleted` |
| Greater than | `field>value` | `?price>100` |
| Less than | `field<value` | `?price<500` |
| Greater or equal | `field>=value` | `?rating>=4` |
| Less or equal | `field<=value` | `?quantity<=10` |

```
GET /api/products?price>100&price<500
GET /api/users?created_at>=2025-01-01
```

---

## Sorting

### Single Field Sort

```
GET /api/users?sort=name              # Ascending
GET /api/users?sort=-created_at       # Descending (prefix with -)
```

### Multiple Field Sort

```
GET /api/users?sort=status,created_at         # Both ascending
GET /api/users?sort=status,-created_at        # Status asc, created_at desc
```

### Alternative Syntax

```
GET /api/users?sort=name:asc
GET /api/users?sort=created_at:desc
```

---

## Searching

### Full-Text Search

Use `q` or `search` for full-text search:

```
GET /api/users?q=john
GET /api/users?search=john
GET /api/products?search=laptop
```

### Field-Specific Search

```
GET /api/users?name=john
GET /api/products?title=iphone&description=apple
```

---

## Field Selection

Allow clients to specify which fields to return:

```
GET /api/users?fields=id,name,email
GET /api/users?fields=id,name,profile.avatar
```

Response:

```json
{
  "data": [
    { "id": "1", "name": "John", "email": "john@example.com" },
    { "id": "2", "name": "Jane", "email": "jane@example.com" }
  ]
}
```

---

## Request Headers

### Content-Type

Always specify the content type:

```
POST /api/users
Content-Type: application/json
{ "name": "John" }
```

### Accept

Use for content negotiation:

```
GET /api/users
Accept: application/json
```

### Authorization

Standard format:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Authorization: ApiKey your-api-key-here
```

### Custom Headers

Use `X-` prefix for custom headers:

```
X-Request-ID: unique-request-id
X-Client-Version: 2.0.0
```

---

## Common Patterns

### Pagination

```
GET /api/users?page=2&per_page=20
```

### Date Range

```
GET /api/orders?created_after=2025-01-01&created_before=2025-01-31
```

### Nested Field Filtering

```
GET /api/users?address.city=NewYork
GET /api/products?specifications.color=red
```
