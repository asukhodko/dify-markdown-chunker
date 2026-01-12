# User Management API

## Overview

The User Management API provides endpoints for managing user accounts, authentication, and permissions in your application. This RESTful API supports JSON requests and responses.

**Base URL:** `https://api.example.com/v1`

**Authentication:** Bearer token required for all endpoints

## Authentication

### Get Access Token

```http
POST /auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password",
  "grant_type": "password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def50200..."
}
```

### Using the Token

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Users

### Create User

Creates a new user account.

```http
POST /users
Content-Type: application/json
Authorization: Bearer {token}

{
  "email": "newuser@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | Yes | User's email address (must be unique) |
| `password` | string | Yes | Password (min 8 characters) |
| `first_name` | string | Yes | User's first name |
| `last_name` | string | Yes | User's last name |
| `role` | string | No | User role: `admin`, `user`, `viewer` (default: `user`) |

**Response (201 Created):**

```json
{
  "id": "usr_1234567890",
  "email": "newuser@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get User

Retrieves user information by ID.

```http
GET /users/{user_id}
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | Unique user identifier |

**Response (200 OK):**

```json
{
  "id": "usr_1234567890",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "status": "active",
  "last_login": "2024-01-15T09:15:00Z",
  "created_at": "2024-01-10T14:20:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### List Users

Retrieves a paginated list of users.

```http
GET /users?page=1&limit=20&role=user&status=active
Authorization: Bearer {token}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number for pagination |
| `limit` | integer | 20 | Number of users per page (max 100) |
| `role` | string | - | Filter by user role |
| `status` | string | - | Filter by status: `active`, `inactive`, `suspended` |
| `search` | string | - | Search in email, first_name, last_name |

**Response (200 OK):**

```json
{
  "users": [
    {
      "id": "usr_1234567890",
      "email": "user1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "status": "active",
      "created_at": "2024-01-10T14:20:00Z"
    },
    {
      "id": "usr_0987654321",
      "email": "user2@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "admin",
      "status": "active",
      "created_at": "2024-01-08T11:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

### Update User

Updates user information.

```http
PUT /users/{user_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "first_name": "John",
  "last_name": "Smith",
  "role": "admin"
}
```

**Response (200 OK):**

```json
{
  "id": "usr_1234567890",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "role": "admin",
  "status": "active",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### Delete User

Soft deletes a user account.

```http
DELETE /users/{user_id}
Authorization: Bearer {token}
```

**Response (204 No Content)**

## Permissions

### Get User Permissions

```http
GET /users/{user_id}/permissions
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "user_id": "usr_1234567890",
  "permissions": [
    {
      "resource": "users",
      "actions": ["read", "create"]
    },
    {
      "resource": "reports",
      "actions": ["read"]
    }
  ]
}
```

### Update User Permissions

```http
PUT /users/{user_id}/permissions
Content-Type: application/json
Authorization: Bearer {token}

{
  "permissions": [
    {
      "resource": "users",
      "actions": ["read", "create", "update"]
    },
    {
      "resource": "reports",
      "actions": ["read", "create"]
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format.

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email address is already in use"
      }
    ]
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request data |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource already exists |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |

## Rate Limiting

API requests are limited to prevent abuse:

- **Authenticated requests:** 1000 requests per hour per user
- **Authentication endpoints:** 10 requests per minute per IP

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## SDK Examples

### Python

```python
import requests

class UserAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def create_user(self, user_data):
        response = requests.post(
            f'{self.base_url}/users',
            json=user_data,
            headers=self.headers
        )
        return response.json()
    
    def get_user(self, user_id):
        response = requests.get(
            f'{self.base_url}/users/{user_id}',
            headers=self.headers
        )
        return response.json()

# Usage
api = UserAPI('https://api.example.com/v1', 'your_token_here')

new_user = api.create_user({
    'email': 'test@example.com',
    'password': 'secure_password',
    'first_name': 'Test',
    'last_name': 'User'
})

print(f"Created user: {new_user['id']}")
```

### JavaScript

```javascript
class UserAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async createUser(userData) {
    const response = await fetch(`${this.baseUrl}/users`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(userData)
    });
    return response.json();
  }

  async getUser(userId) {
    const response = await fetch(`${this.baseUrl}/users/${userId}`, {
      headers: this.headers
    });
    return response.json();
  }
}

// Usage
const api = new UserAPI('https://api.example.com/v1', 'your_token_here');

const newUser = await api.createUser({
  email: 'test@example.com',
  password: 'secure_password',
  first_name: 'Test',
  last_name: 'User'
});

console.log(`Created user: ${newUser.id}`);
```

## Webhooks

Configure webhooks to receive real-time notifications about user events.

### Webhook Events

| Event | Description |
|-------|-------------|
| `user.created` | New user account created |
| `user.updated` | User information updated |
| `user.deleted` | User account deleted |
| `user.login` | User logged in |
| `user.logout` | User logged out |

### Webhook Payload

```json
{
  "event": "user.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "user": {
      "id": "usr_1234567890",
      "email": "newuser@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user"
    }
  }
}
```

### Webhook Configuration

```http
POST /webhooks
Content-Type: application/json
Authorization: Bearer {token}

{
  "url": "https://your-app.com/webhooks/users",
  "events": ["user.created", "user.updated"],
  "secret": "your_webhook_secret"
}
```

## Testing

Use our sandbox environment for testing:

**Sandbox Base URL:** `https://api-sandbox.example.com/v1`

### Test Credentials

```json
{
  "username": "test@example.com",
  "password": "test_password"
}
```

### Postman Collection

Download our Postman collection: [User API Collection](https://api.example.com/postman/user-api.json)

## Support

- **Documentation:** https://docs.example.com/api
- **Status Page:** https://status.example.com
- **Support Email:** api-support@example.com
- **GitHub Issues:** https://github.com/example/user-api/issues