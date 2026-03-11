---
title: Advanced Operations
impact: MEDIUM
tags: bulk, batch, idempotency, partial-update
---

# Advanced Operations

## Bulk Operations

### Bulk Create

```
POST /api/users/batch
{
  "items": [
    { "name": "User1", "email": "user1@example.com" },
    { "name": "User2", "email": "user2@example.com" },
    { "name": "User3", "email": "user3@example.com" }
  ]
}

{
  "results": [
    { "index": 0, "id": "1", "status": "created" },
    { "index": 1, "id": "2", "status": "created" },
    { "index": 2, "status": "failed", "error": "Email already exists" }
  ],
  "summary": {
    "total": 3,
    "created": 2,
    "failed": 1
  }
}
```

### Bulk Update

```
PATCH /api/users/batch
{
  "updates": [
    { "id": "1", "status": "active" },
    { "id": "2", "status": "inactive" }
  ]
}

{
  "results": [
    { "id": "1", "status": "updated" },
    { "id": "2", "status": "updated" }
  ]
}
```

### Bulk Delete

```
POST /api/users/batch-delete
{
  "ids": ["1", "2", "3"]
}

{
  "deleted_count": 3
}
```

---

## Idempotency

### Idempotency Key

Support `Idempotency-Key` header for POST operations:

```
POST /api/orders
Idempotency-Key: unique-key-123
{
  "items": [...]
}

→ 201 Created
{
  "id": "order-123",
  "status": "pending"
}
```

If the same request is retried with the same key:

```
POST /api/orders
Idempotency-Key: unique-key-123
{ "items": [...] }

→ 200 OK
{
  "id": "order-123",
  "status": "pending"
}
```

**Key Points:**

- Store the response with the idempotency key
- Return cached response on duplicate requests
- Set reasonable TTL (e.g., 24-48 hours)
- Use a unique key per operation

---

## Partial Updates

### PUT vs PATCH

- **PUT**: Replace entire resource
- **PATCH**: Partial update

### PUT (Full Replacement)

```
PUT /api/users/123
{
  "id": "123",
  "name": "Jane",
  "email": "jane@example.com",
  "status": "active"
}

// All fields required
```

### PATCH (Partial Update)

```
PATCH /api/users/123
{
  "name": "Jane"
}

// Only specified fields updated
```

### JSON Patch Format

```
PATCH /api/users/123
Content-Type: application/json-patch+json

[
  { "op": "replace", "path": "/name", "value": "Jane" },
  { "op": "remove", "path": "/status" }
]
```

### JSON Merge Patch

```
PATCH /api/users/123
Content-Type: application/merge-patch+json

{
  "name": "Jane",
  "email": "jane@example.com"
}
```

---

## Field Selection

Allow clients to request specific fields:

```
GET /api/users/123?fields=id,name,email

{
  "data": {
    "id": "123",
    "name": "John",
    "email": "john@example.com"
  }
}
```

Use dot notation for nested fields:

```
GET /api/users/123?fields=id,name,profile.avatar
```

---

## Action Endpoints

For non-CRUD operations, use action endpoints:

```
POST /api/users/123/activate
POST /api/users/123/deactivate
POST /api/orders/123/cancel
POST /api/orders/123/ship
POST /api/posts/123/publish
POST /api/posts/123/unpublish
```

---

## Batch Processing Limits

Set reasonable limits on bulk operations:

```
POST /api/users/batch
{
  "items": [
    // Max 100 items per request
  ]
}
```

Return error if limit exceeded:

```json
{
  "error": {
    "code": "BATCH_LIMIT_EXCEEDED",
    "message": "Maximum 100 items per batch",
    "limit": 100
  }
}
```
