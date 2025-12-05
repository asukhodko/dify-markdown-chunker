"""Comprehensive generator for all missing corpus categories."""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .base import BaseGenerator, CollectionResult, DocumentMetadata


class ComprehensiveGenerator(BaseGenerator):
    """Generator for technical docs, changelogs, and blogs."""

    def __init__(self, output_dir: Path, category: str, subcategory: str = None):
        super().__init__(output_dir)
        self.category = category
        self.subcategory = subcategory

    def generate(self, count: int) -> List[CollectionResult]:
        """Generate documents for the category."""
        results = []
        
        print(f"Generating {count} {self.category} documents...")
        
        for i in range(count):
            try:
                if self.category == "technical_docs":
                    content = self._generate_technical_doc(i)
                elif self.category == "github_readmes":
                    content = self._generate_github_readme(i)
                elif self.category == "changelogs":
                    content = self._generate_changelog(i)
                elif self.category == "engineering_blogs":
                    content = self._generate_engineering_blog(i)
                else:
                    content = self._generate_generic(i)
                
                # Analyze and create metadata
                analysis = self._analyze_content(content)
                filename = self._generate_filename(i)
                
                metadata = DocumentMetadata(
                    filename=filename,
                    category=self.category,
                    subcategory=self.subcategory,
                    size_bytes=len(content.encode("utf-8")),
                    source="synthetic",
                    collection_date=datetime.now().isoformat(),
                    content_hash=self._compute_hash(content),
                    **analysis,
                )
                
                metadata.expected_strategy = self._determine_expected_strategy(analysis)
                
                if self.save_document(content, filename, metadata):
                    results.append(
                        CollectionResult(success=True, content=content, metadata=metadata)
                    )
                    print(f"  ✓ {filename}")
                else:
                    results.append(CollectionResult(success=False, error="Failed to save"))
                    print(f"  ✗ {filename}")
                    
            except Exception as e:
                print(f"  ✗ Error generating document {i}: {str(e)}")
                results.append(CollectionResult(success=False, error=str(e)))
        
        return results

    def _generate_filename(self, index: int) -> str:
        """Generate filename."""
        if self.subcategory:
            return f"{self.subcategory}_{index:03d}.md"
        return f"{self.category}_{index:03d}.md"

    def _generate_technical_doc(self, index: int) -> str:
        """Generate technical documentation."""
        projects = ["Kubernetes", "Docker", "React", "AWS", "PostgreSQL", "Redis", "Nginx", "Terraform"]
        topics = ["Getting Started", "Configuration", "API Reference", "Best Practices", "Troubleshooting"]
        
        project = random.choice(projects)
        topic = random.choice(topics)
        
        # Vary size significantly
        size_multiplier = random.choice([1, 2, 3, 5, 8])
        
        content = f"""# {project} {topic}

## Overview

{project} is a powerful tool for modern infrastructure. This guide covers {topic.lower()} 
for production deployments.

## Prerequisites

Before you begin, ensure you have:

- System requirements met
- Required permissions
- Network access configured

## Installation

### Quick Start

```bash
# Install {project.lower()}
curl -fsSL https://install.example.com | sh

# Verify installation
{project.lower()} --version
```

### Configuration

Create a configuration file:

```yaml
# config.yaml
apiVersion: v1
kind: Config
metadata:
  name: {project.lower()}-config
spec:
  replicas: 3
  resources:
    cpu: "100m"
    memory: "128Mi"
```

## Basic Usage

### Creating Resources

```bash
# Create a new resource
{project.lower()} create -f resource.yaml

# List all resources
{project.lower()} list

# Get resource details
{project.lower()} describe <resource-name>
```

### Common Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| Create | `{project.lower()} create` | Create new resource |
| Update | `{project.lower()} apply` | Update existing resource |
| Delete | `{project.lower()} delete` | Remove resource |
| List | `{project.lower()} list` | Show all resources |

## Advanced Configuration

### Performance Tuning

```yaml
performance:
  cache_size: 1024MB
  max_connections: 1000
  timeout: 30s
  retry_attempts: 3
```

### Security Settings

```yaml
security:
  enable_tls: true
  auth_method: oauth2
  permissions:
    - read
    - write
    - admin
```

## API Reference

### Core APIs

#### Create Resource

```http
POST /api/v1/resources
Content-Type: application/json

{{
  "name": "example",
  "type": "standard",
  "config": {{}}
}}
```

Response:

```json
{{
  "id": "res-12345",
  "name": "example",
  "status": "created",
  "created_at": "2024-01-01T00:00:00Z"
}}
```

#### List Resources

```http
GET /api/v1/resources?filter=active&limit=10
```

### Authentication

Use API keys for authentication:

```bash
export {project.upper()}_API_KEY=your-api-key
{project.lower()} --auth-key ${{project.upper()}}_API_KEY list
```

## Monitoring

### Metrics

Key metrics to monitor:

- Request rate
- Error rate  
- Latency (p50, p95, p99)
- Resource utilization

```python
from {project.lower()}_sdk import Metrics

metrics = Metrics()
print(f"Request rate: {{metrics.request_rate()}} req/s")
print(f"Error rate: {{metrics.error_rate()}}%")
```

### Logging

Configure logging levels:

```yaml
logging:
  level: info
  format: json
  outputs:
    - stdout
    - /var/log/{project.lower()}.log
```

"""
        
        # Add more sections for larger documents
        if size_multiplier >= 2:
            content += """
## Best Practices

### Development

1. Use version control for all configurations
2. Test changes in staging environment
3. Implement proper error handling
4. Monitor resource usage

### Production

1. Enable high availability
2. Set up automated backups
3. Configure monitoring and alerting
4. Implement security best practices

### Performance

- Enable caching where appropriate
- Use connection pooling
- Optimize database queries
- Monitor and tune resource limits

"""
        
        if size_multiplier >= 3:
            content += """
## Troubleshooting

### Common Issues

#### Connection Timeout

**Symptom**: Requests timeout after 30 seconds

**Solution**:

```bash
# Increase timeout
{project.lower()} config set timeout 60s

# Check network connectivity
ping backend.example.com
```

#### High Memory Usage

**Symptom**: Memory usage above 80%

**Solution**:

```bash
# Check current usage
{project.lower()} stats memory

# Adjust limits
{project.lower()} config set memory_limit 2GB
```

#### Permission Denied

**Symptom**: "Permission denied" errors

**Solution**:

```bash
# Check permissions
{project.lower()} auth check

# Grant required permissions
{project.lower()} auth grant --role admin
```

"""
        
        if size_multiplier >= 5:
            content += f"""
## Migration Guide

### From Previous Version

Steps to migrate from v1 to v2:

1. **Backup existing data**

```bash
{project.lower()} backup create --output backup.tar.gz
```

2. **Update configuration**

```bash
# Convert old config
{project.lower()} config convert v1-config.yaml > v2-config.yaml
```

3. **Run migration**

```bash
{project.lower()} migrate --from v1 --to v2
```

4. **Verify migration**

```bash
{project.lower()} validate
```

### Breaking Changes

- API endpoint structure changed
- Configuration format updated
- Deprecated features removed

## Examples

### Example 1: Basic Setup

```python
from {project.lower()} import Client

client = Client(api_key="your-key")
resource = client.create_resource(
    name="example",
    type="standard"
)
print(f"Created: {{resource.id}}")
```

### Example 2: Advanced Usage

```python
from {project.lower()} import Client, Config

config = Config(
    timeout=60,
    retries=3,
    cache_enabled=True
)

client = Client(config=config)

# Batch operations
resources = client.batch_create([
    {{"name": "res1", "type": "standard"}},
    {{"name": "res2", "type": "premium"}},
])

for res in resources:
    print(f"Created {{res.name}}: {{res.status}}")
```

### Example 3: Error Handling

```python
from {project.lower()} import Client, {project}Error

client = Client()

try:
    resource = client.get_resource("invalid-id")
except {project}Error as e:
    print(f"Error: {{e.message}}")
    print(f"Code: {{e.code}}")
    # Handle error appropriately
```

"""
        
        content += """
## Additional Resources

- Official Documentation: https://docs.example.com
- Community Forum: https://forum.example.com
- GitHub Repository: https://github.com/example/project
- API Reference: https://api.example.com/docs

## Support

For help and support:

- GitHub Issues: https://github.com/example/project/issues
- Stack Overflow: Tag `example-project`
- Slack Community: https://slack.example.com

---

Last updated: """ + datetime.now().strftime("%Y-%m-%d")
        
        return content

    def _generate_github_readme(self, index: int) -> str:
        """Generate GitHub README-like document."""
        project_names = ["awesome-lib", "super-tool", "mega-framework", "ultra-cli", 
                        "hyper-api", "quantum-db", "stellar-ui", "cosmic-backend"]
        languages = ["Python", "JavaScript", "Go", "Rust", "TypeScript"]
        
        project = random.choice(project_names)
        lang = random.choice(languages)
        
        content = f"""# {project}

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](CHANGELOG.md)
[![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://ci.example.com)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://codecov.io)

> A modern {lang} library for building amazing applications

## ✨ Features

- 🚀 **Fast**: Optimized for performance
- 🔒 **Secure**: Built with security in mind
- 📦 **Lightweight**: Minimal dependencies
- 🎨 **Customizable**: Flexible configuration
- 📚 **Well-documented**: Comprehensive docs
- 🧪 **Tested**: 95%+ coverage

## 🚀 Quick Start

### Installation

```bash
# Using npm
npm install {project}

# Using yarn
yarn add {project}

# Using pip (if Python)
pip install {project}
```

### Basic Usage

```{lang.lower()}
// Import the library
const {project.replace('-', '')} = require('{project}');

// Initialize
const client = new {project.replace('-', '').title()}({{
    apiKey: 'your-api-key',
    timeout: 30000
}});

// Use it
const result = await client.doSomething();
console.log(result);
```

## 📖 Documentation

### API Reference

#### Constructor

```{lang.lower()}
new {project.replace('-', '').title()}(options)
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | Your API key |
| `timeout` | number | 30000 | Request timeout in ms |
| `retries` | number | 3 | Number of retry attempts |
| `debug` | boolean | false | Enable debug mode |

#### Methods

##### `doSomething()`

Performs the main operation.

```{lang.lower()}
const result = await client.doSomething(params);
```

**Parameters:**

- `params` (Object): Configuration parameters

**Returns:** Promise<Result>

### Examples

#### Example 1: Basic Usage

```{lang.lower()}
const client = new {project.replace('-', '').title()}({{
    apiKey: process.env.API_KEY
}});

const data = await client.getData();
console.log(data);
```

#### Example 2: Advanced Configuration

```{lang.lower()}
const client = new {project.replace('-', '').title()}({{
    apiKey: process.env.API_KEY,
    timeout: 60000,
    retries: 5,
    hooks: {{
        beforeRequest: (config) => console.log('Request:', config),
        afterResponse: (response) => console.log('Response:', response)
    }}
}});
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Clone repository
git clone https://github.com/user/{project}.git
cd {project}

# Install dependencies
npm install

# Run tests
npm test

# Build
npm run build
```

### Running Tests

```bash
# Unit tests
npm run test:unit

# Integration tests
npm run test:integration

# Coverage
npm run test:coverage
```

## 📊 Benchmarks

Performance comparison with alternatives:

| Library | Operations/sec | Memory (MB) |
|---------|----------------|-------------|
| {project} | 10,000 | 50 |
| alternative-a | 8,000 | 75 |
| alternative-b | 6,500 | 100 |

## 🗺️ Roadmap

- [x] Core functionality
- [x] TypeScript support
- [x] Comprehensive tests
- [ ] Plugin system
- [ ] CLI tool
- [ ] GraphQL support
- [ ] Real-time updates

## 📜 License

MIT © [Author Name](https://github.com/author)

## 🙏 Acknowledgments

- Thanks to all [contributors](https://github.com/user/{project}/graphs/contributors)
- Inspired by [similar-project](https://github.com/similar/project)
- Built with [awesome-tool](https://example.com)

## 📞 Support

- 📧 Email: support@example.com
- 💬 Discord: https://discord.gg/example
- 🐦 Twitter: [@example](https://twitter.com/example)
"""
        
        return content

    def _generate_changelog(self, index: int) -> str:
        """Generate a changelog document."""
        versions = [(2, i) for i in range(5, -1, -1)] + [(1, i) for i in range(9, -1, -1)]
        
        content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        content += "The format is based on [Keep a Changelog](https://keepachangelog.com/),\n"
        content += "and this project adheres to [Semantic Versioning](https://semver.org/).\n\n"
        
        for major, minor in versions[:random.randint(5, 12)]:
            date = datetime.now() - timedelta(days=random.randint(30, 365))
            version = f"{major}.{minor}.0"
            
            content += f"## [{version}] - {date.strftime('%Y-%m-%d')}\n\n"
            
            if random.random() < 0.8:
                content += "### Added\n\n"
                for i in range(random.randint(1, 4)):
                    content += f"- New feature {i+1} implementation\n"
                    content += f"- Support for additional configuration options\n"
                content += "\n"
            
            if random.random() < 0.7:
                content += "### Changed\n\n"
                for i in range(random.randint(1, 3)):
                    content += f"- Updated dependency to version {major}.{minor+i}\n"
                    content += f"- Improved performance of core operations\n"
                content += "\n"
            
            if random.random() < 0.6:
                content += "### Fixed\n\n"
                for i in range(random.randint(1, 3)):
                    content += f"- Fixed bug #{{random.randint(100, 999)}} in module\n"
                    content += f"- Resolved memory leak in background process\n"
                content += "\n"
            
            if random.random() < 0.3:
                content += "### Removed\n\n"
                content += "- Deprecated API endpoints\n"
                content += "- Legacy compatibility code\n\n"
            
            if random.random() < 0.2:
                content += "### Security\n\n"
                content += "- Fixed security vulnerability CVE-2024-XXXX\n"
                content += "- Updated authentication mechanism\n\n"
        
        return content

    def _generate_engineering_blog(self, index: int) -> str:
        """Generate engineering blog post."""
        topics = [
            ("Scaling", "microservices to handle 1M requests/second"),
            ("Optimizing", "database queries for 10x performance improvement"),
            ("Building", "real-time data pipeline with Apache Kafka"),
            ("Migrating", "monolith to microservices architecture"),
            ("Implementing", "zero-downtime deployment strategy"),
            ("Designing", "distributed caching layer with Redis"),
        ]
        
        action, description = random.choice(topics)
        
        content = f"""# {action} Our Infrastructure: {description}

*Posted on {datetime.now().strftime('%B %d, %Y')} by Engineering Team*

## Introduction

Over the past year, our platform has experienced tremendous growth. This post 
details our journey {action.lower()} {description}.

## The Challenge

As our user base grew from 10K to 1M+ users, we faced several challenges:

- **Performance**: Response times increased to 2-3 seconds
- **Scalability**: Single server couldn't handle peak load
- **Reliability**: Downtime during deployments
- **Cost**: Infrastructure costs growing faster than revenue

## Initial Architecture

Our original setup:

```
┌─────────────┐
│   Client    │
└─────────────┘
       │
       ▼
┌─────────────┐
│  Web Server │
│  (Single)   │
└─────────────┘
       │
       ▼
┌─────────────┐
│  PostgreSQL │
│  (Primary)  │
└─────────────┘
```

## Solution Design

After extensive research and prototyping, we designed a new architecture:

```
┌─────────────┐
│Load Balancer│
└─────────────┘
       │
    ┌──┴──┐
    ▼     ▼
┌─────┐ ┌─────┐
│Web-1│ │Web-2│ ...
└─────┘ └─────┘
    │     │
    └──┬──┘
       ▼
┌─────────────┐
│   Redis     │
│   Cache     │
└─────────────┘
       │
       ▼
┌─────────────┐
│  PostgreSQL │
│  (Primary)  │
└─────────────┘
```

## Implementation

### Phase 1: Infrastructure Setup

```bash
# Set up Kubernetes cluster
kubectl create namespace production

# Deploy Redis
helm install redis bitnami/redis \\
    --set auth.password=$REDIS_PASSWORD \\
    --set replica.replicaCount=3
```

### Phase 2: Application Changes

```python
# Before: Direct database queries
def get_user(user_id):
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

# After: Cache-first approach
def get_user(user_id):
    # Try cache first
    cached = redis.get(f"user:{{user_id}}")
    if cached:
        return json.loads(cached)
    
    # Fallback to database
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # Cache for 5 minutes
    redis.setex(f"user:{{user_id}}", 300, json.dumps(user))
    
    return user
```

### Phase 3: Monitoring

```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.route('/api/data')
@request_duration.time()
def get_data():
    request_count.inc()
    return fetch_data()
```

## Results

### Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| P50 Latency | 800ms | 95ms | -88% |
| P99 Latency | 3.2s | 250ms | -92% |
| Throughput | 100 req/s | 5000 req/s | +4900% |
| Error Rate | 2.5% | 0.1% | -96% |

### Cost Analysis

- Infrastructure cost increased by 40%
- Revenue increased by 200%
- Cost per user decreased by 50%

## Lessons Learned

1. **Measure First**: Extensive profiling revealed surprising bottlenecks
2. **Iterate Quickly**: We deployed incrementally over 3 months
3. **Monitor Everything**: Metrics were crucial for optimization
4. **Team Alignment**: Regular syncs kept everyone informed

## Challenges

### Cache Invalidation

Cache invalidation proved tricky. We implemented a pub/sub pattern:

```python
# Publisher (on data update)
def update_user(user_id, data):
    db.update("users", user_id, data)
    redis.publish('user_updates', json.dumps({{
        'id': user_id,
        'action': 'update'
    }}))

# Subscriber (cache invalidator)
def handle_update(message):
    data = json.loads(message)
    redis.delete(f"user:{{data['id']}}")
```

### Database Migration

Zero-downtime migration required careful planning:

1. Set up replication
2. Switch reads to replica
3. Migrate writes
4. Promote replica to primary

## Future Work

- Implement database sharding for further scaling
- Add CDN for static assets
- Explore serverless for batch jobs
- Improve observability with distributed tracing

## Conclusion

This project significantly improved our platform's performance and reliability.
The key was methodical planning, incremental rollout, and comprehensive monitoring.

---

*Want to work on these challenges? We're hiring! Check out our [careers page](https://example.com/careers).*
"""
        
        return content

    def _generate_generic(self, index: int) -> str:
        """Generate generic document."""
        return f"""# Generic Document {index}

## Introduction

This is a generic markdown document.

## Content

Sample content here.

## Conclusion

End of document.
"""
