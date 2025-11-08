# API Documentation Guide

## Authentication

### Admin Login
```http
POST /admin/admin-login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token"
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "detail": "Invalid credentials"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Provide valid credentials |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify resource exists |
| 422 | Validation Error | Fix request data |
| 429 | Rate Limited | Reduce request frequency |
| 500 | Server Error | Contact support |

## Rate Limits

- **Authentication**: 5 requests/minute
- **General API**: 100 requests/minute
- **File Upload**: 10 requests/minute

## Headers

**Required:**
```http
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Optional:**
```http
X-Request-ID: unique-request-id
User-Agent: your-app/1.0
```