# REST API Documentation

Version: 2.0.0
Author: API Team
Date: 2025-11-16

## Overview

This document describes the REST API endpoints for the User Management Service. The API follows RESTful principles and uses JSON for request and response payloads.

## Authentication

All API requests require authentication using Bearer tokens:

```http
Authorization: Bearer <your-token-here>
```

### Getting a Token

```python
import requests

response = requests.post('https://api.example.com/auth/token', json={
    'username': 'user@example.com',
    'password': 'secure_password'
})

token = response.json()['access_token']
```

## Endpoints

### Users

#### List Users

Get a paginated list of all users.

**Endpoint:** `GET /api/v2/users`

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20, max: 100)
- `sort` (string, optional): Sort field (default: "created_at")
- `order` (string, optional): Sort order - "asc" or "desc" (default: "desc")

**Response:**

```json
{
  "data": [
    {
      "id": "usr_123abc",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "admin",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-11-16T14:20:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

**Example:**

```python
import requests

headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'https://api.example.com/api/v2/users',
    headers=headers,
    params={'page': 1, 'limit': 50}
)

users = response.json()['data']
for user in users:
    print(f"{user['name']} ({user['email']})")
```

#### Get User

Retrieve a specific user by ID.

**Endpoint:** `GET /api/v2/users/{user_id}`

**Path Parameters:**
- `user_id` (string, required): User ID

**Response:**

```json
{
  "id": "usr_123abc",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "profile": {
    "avatar_url": "https://cdn.example.com/avatars/123.jpg",
    "bio": "Software engineer",
    "location": "San Francisco, CA"
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-11-16T14:20:00Z"
}
```

**Example:**

```python
response = requests.get(
    f'https://api.example.com/api/v2/users/usr_123abc',
    headers=headers
)

user = response.json()
print(f"User: {user['name']}")
print(f"Role: {user['role']}")
```

#### Create User

Create a new user account.

**Endpoint:** `POST /api/v2/users`

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "password": "secure_password_123",
  "role": "user"
}
```

**Response:** `201 Created`

```json
{
  "id": "usr_456def",
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "role": "user",
  "created_at": "2025-11-16T15:00:00Z"
}
```

**Example:**

```python
new_user = {
    'email': 'jane@example.com',
    'name': 'Jane Smith',
    'password': 'SecurePass123!',
    'role': 'user'
}

response = requests.post(
    'https://api.example.com/api/v2/users',
    headers=headers,
    json=new_user
)

if response.status_code == 201:
    user_id = response.json()['id']
    print(f"User created with ID: {user_id}")
```

#### Update User

Update an existing user's information.

**Endpoint:** `PATCH /api/v2/users/{user_id}`

**Request Body:**

```json
{
  "name": "John Updated",
  "profile": {
    "bio": "Senior Software Engineer"
  }
}
```

**Response:** `200 OK`

```json
{
  "id": "usr_123abc",
  "email": "user@example.com",
  "name": "John Updated",
  "role": "admin",
  "profile": {
    "bio": "Senior Software Engineer"
  },
  "updated_at": "2025-11-16T15:30:00Z"
}
```

#### Delete User

Delete a user account.

**Endpoint:** `DELETE /api/v2/users/{user_id}`

**Response:** `204 No Content`

**Example:**

```python
response = requests.delete(
    f'https://api.example.com/api/v2/users/usr_123abc',
    headers=headers
)

if response.status_code == 204:
    print("User deleted successfully")
```

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Invalid request data |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

## Rate Limiting

API requests are rate-limited to 1000 requests per hour per user. Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1700150400
```

## Webhooks

Configure webhooks to receive real-time notifications about events:

```python
webhook_config = {
    'url': 'https://your-app.com/webhooks/users',
    'events': ['user.created', 'user.updated', 'user.deleted'],
    'secret': 'your_webhook_secret'
}

response = requests.post(
    'https://api.example.com/api/v2/webhooks',
    headers=headers,
    json=webhook_config
)
```

## SDK Support

Official SDKs are available for:
- Python: `pip install example-api-client`
- JavaScript: `npm install @example/api-client`
- Ruby: `gem install example-api`
- Go: `go get github.com/example/api-go`

## Support

For API support, contact api-support@example.com or visit our developer portal at https://developers.example.com
