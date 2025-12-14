# User API Reference

## GET /users/{id}

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | yes | User ID |
| fields | string | no | Comma-separated list of fields |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | User ID |
| name | string | User name |
| email | string | Email address |
| created_at | datetime | Creation timestamp |

### Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 404 | Not Found | User does not exist |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing authentication |

## POST /users

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | User name |
| email | string | yes | Email address |
| password | string | yes | Password (min 8 chars) |

### Response

| Field | Type | Description |
|-------|------|-------------|
| id | string | Created user ID |
| name | string | User name |
| email | string | Email address |
