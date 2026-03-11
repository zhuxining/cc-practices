---
title: API Versioning
impact: MEDIUM
tags: versioning, url, header, deprecation
---

# API Versioning

## URL Versioning (Recommended)

Include version in the URL path:

```
/api/v1/users
/api/v2/users
```

**Pros:**

- Clear and visible
- Easy to route and test
- Straightforward documentation

**Cons:**

- Multiple URLs for same resource
- URL changes between versions

**Guidelines:**

- Use major version only (v1, v2, not v1.2)
- Place version after `/api/`
- Maintain old versions for 6-12 months

```
/api/v1/users          # Version 1
/api/v2/users          # Version 2 (may have breaking changes)
```

---

## Header Versioning

Use custom header for versioning:

```
GET /api/users
API-Version: 2

or

GET /api/users
Accept: application/vnd.api.v2+json
```

**Pros:**

- Clean URLs
- Same URL across versions

**Cons:**

- Less visible
- Harder to test in browser
- Easy to forget version header

---

## Query Parameter Versioning

```
GET /api/users?version=2
GET /api/users?v=2
```

**Pros:**

- Easy to test
- Optional (can default to latest)

**Cons:**

- Parameter can be forgotten
- Not as explicit as URL versioning

---

## Best Practices

### When to Version

Version only for **breaking changes**:

- Removing or renaming fields
- Changing data types
- Modifying request/response structure
- Changing required parameters

**Don't version for:**

- Adding new optional fields
- Adding new endpoints
- Bug fixes
- Performance improvements

### Backward Compatibility

Maintain old versions:

```
/api/v1/users          # Deprecated but available until 2025-12-31
/api/v2/users          # Current stable version
/api/v3/users          # Beta/preview version
```

### Deprecation Headers

Inform clients about deprecated endpoints:

```
GET /api/v1/users

X-API-Deprecated: true
X-API-Sunset: 2026-01-01
X-API-Alternative: /api/v2/users
Link: </api/v2/users>; rel="successor-version"
```

### Version Discovery

Provide endpoint to check available versions:

```
GET /api/versions

{
  "versions": [
    {
      "version": "v1",
      "status": "deprecated",
      "sunset_date": "2026-01-01"
    },
    {
      "version": "v2",
      "status": "stable",
      "latest": true
    }
  ]
}
```

---

## Migration Guide

### Example: Changing Field Name

**v1 Response:**

```json
{
  "user_name": "John",
  "user_email": "john@example.com"
}
```

**v2 Response:**

```json
{
  "name": "John",
  "email": "john@example.com"
}
```

**Migration Approach:**

1. Add new fields in v1 (mark old as deprecated):

```json
{
  "user_name": "John",
  "user_email": "john@example.com",
  "name": "John",
  "email": "john@example.com"
}
```

1. Release v2 with new format only

2. Deprecate v1 after 6-12 months

---

## Version-Specific Documentation

Document differences between versions:

```
GET /api/v2/docs

{
  "changes_from_v1": [
    {
      "type": "breaking",
      "description": "Renamed user_name to name"
    },
    {
      "type": "feature",
      "description": "Added filter by created_at"
    }
  ]
}
```

Reference: [Semantic Versioning](https://semver.org/)
