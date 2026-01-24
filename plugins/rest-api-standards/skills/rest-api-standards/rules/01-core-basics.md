---
title: Core Basics - HTTP Methods & URI Design
impact: CRITICAL
tags: http, methods, uri, naming, structure
---

# HTTP Methods and URI Design

## HTTP Methods

### Use Nouns for Resources

Use nouns to represent resources. The HTTP method indicates the action.

```
GET    /users              # List all users
POST   /users              # Create a new user
GET    /users/123          # Get user 123
PUT    /users/123          # Replace user 123
PATCH  /users/123          # Partially update user 123
DELETE /users/123          # Delete user 123
```

### HTTP Method Mapping

| Operation | HTTP Method | Idempotent | Safe |
|-----------|-------------|------------|------|
| Create | POST | No | No |
| Read | GET | Yes | Yes |
| Update (full) | PUT | Yes | No |
| Update (partial) | PATCH | No | No |
| Delete | DELETE | Yes | No |

### Idempotency

- **PUT and DELETE are idempotent**: Multiple identical requests have the same effect
- **POST is not idempotent**: Each call may create a new resource

### Safe Methods

- **GET, HEAD, OPTIONS** must not modify server state
- Use appropriate methods (POST, PUT, PATCH, DELETE) for state changes

---

## URI Naming

### Use Kebab-Case for Multi-Word Resources

```
GET /api/user-profiles
GET /api/order-items
GET /api/blog-posts
```

### Use Plural Nouns for Collections

```
GET /api/users              # Collection endpoint
GET /api/users/123          # Single resource by ID
```

### Use Lowercase Throughout

URLs are case-sensitive in some systems. Always use lowercase:

```
GET /api/users
GET /api/user-profiles
```

### Avoid Verbs in URI Paths

The HTTP method already indicates the action:

```
GET    /users              # Not /getUsers
POST   /users              # Not /createUser
PUT    /users/123          # Not /updateUser/123
DELETE /users/123          # Not /deleteUser/123
```

**Exception**: For non-CRUD operations, use sub-resources:

```
POST /api/users/123/messages     # Send message
POST /api/orders/123/cancel      # Cancel order
```

---

## URI Structure

### Reflect Resource Hierarchy

```
GET /api/users                          # All users
GET /api/users/123                      # User 123
GET /api/users/123/orders               # Orders for user 123
GET /api/users/123/orders/456           # Specific order
```

### Limit Nesting Depth

Keep nesting shallow (max 3-4 levels):

```
# Acceptable (3 levels)
GET /api/users/123/orders/456

# Prefer direct access for deep resources
GET /api/order-items/789
```

### Use Query Parameters for Filtering

Don't create separate endpoints for filters:

```
# Good - single endpoint with filters
GET /api/users?status=active&role=admin

# Bad - combinatorial explosion
GET /api/users/active
GET /api/users/admin
```

**Common Query Parameters:**

| Purpose | Parameter | Example |
|---------|-----------|---------|
| Filtering | `?status=active` | `GET /users?status=active` |
| Multiple filters | `&` | `GET /users?status=active&role=admin` |
| Sorting (asc) | `?sort=field` | `GET /users?sort=name` |
| Sorting (desc) | `?sort=-field` | `GET /users?sort=-created_at` |
| Searching | `?search=term` | `GET /users?search=john` |
| Field selection | `?fields=a,b` | `GET /users?fields=id,name` |
| Pagination | `?page=1&per_page=20` | `GET /users?page=2&per_page=20` |

Reference: [RFC 9110 - HTTP Semantics](https://httpwg.org/specs/rfc9110.html)
