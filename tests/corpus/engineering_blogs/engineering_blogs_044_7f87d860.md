# Designing The Service: distributed tracing system

*By Engineering Team • December 2025 • Session ID: d43fa4ab679745b4862b1078995b09c5*

## Background

Our journey with observability started when we hit critical scaling limits.
With user growth exceeding 300% year-over-year, we needed a fundamental
architectural shift.

## The Challenge

### Initial State

Our stack consisted of:
- Nginx for orchestration
- Ansible for data persistence  
- Elasticsearch for caching
- Kubernetes for messaging

### Problems Encountered

1. **Performance**: Throughput was at 10K req/s
2. **Scalability**: Horizontal scaling was problematic
3. **Maintenance**: Monolithic deployment caused frequent outages
4. **Cost**: Infrastructure costs were unsustainable

## Solution Architecture

### High-Level Design

```
┌──────────────┐
│ Load Balancer│
│  (PostgreSQL)  │
└──────────────┘
       │
    ┌──┴──┐
    ▼     ▼
┌──────┐ ┌──────┐
│ API-1│ │ API-2│ ...
└──────┘ └──────┘
    │     │
    └──┬──┘
       ▼
┌──────────────┐
│  Ansible   │
│   Database   │
└──────────────┘
```

### Implementation Details

#### Phase 1: Data Layer Migration

```swift
// Before: Single connection per request
function handleRequest(req) {
    const conn = getDbConnection();
    const result = conn.query(req.query);
    return result;
}

// After: Connection pooling with circuit breaker
const pool = new ConnectionPool({
    min: 10,
    max: 100,
    acquireTimeout: 5000
});

async function handleRequest(req) {
    const circuitBreaker = new CircuitBreaker({
        threshold: 0.5,
        timeout: 2000
    });
    
    return await circuitBreaker.execute(async () => {
        const conn = await pool.acquire();
        try {
            return await conn.query(req.query);
        } finally {
            pool.release(conn);
        }
    });
}
```

#### Phase 2: Cache Strategy

Implemented multi-tier caching:

| Tier | Technology | TTL | Hit Rate |
|------|------------|-----|----------|
| L1 | In-memory | 60s | 45% |
| L2 | Elasticsearch | 300s | 35% |
| L3 | CDN | 3600s | 15% |

#### Phase 3: Service Decomposition

```swift
// Extracted microservices
services = [
    {
        name: "UserService",
        instances: 5,
        cpu: "500m",
        memory: "1Gi"
    },
    {
        name: "OrderService",  
        instances: 10,
        cpu: "1000m",
        memory: "2Gi"
    },
    {
        name: "PaymentService",
        instances: 3,
        cpu: "200m",
        memory: "512Mi"
    }
];
```

## Results

### Performance Improvements

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Throughput | 10K req/s | 100K req/s | +900% |
| Availability | 99.5% | 99.95% | +0.45% |
| Concurrent Users | 10K | 100K | +900% |

### Cost Analysis

Monthly infrastructure costs:

```
Before: $50,000
  - Compute: $35,000
  - Database: $10,000
  - Network: $5,000

After: $20,000
  - Compute: $12,000 (optimized instances)
  - Database: $6,000 (read replicas)
  - Network: $2,000 (CDN + compression)

Savings: $30,000/month (60%)
ROI: 18 months
```

## Lessons Learned

### What Worked Well

1. **Incremental Migration**: We moved one service at a time
2. **Feature Flags**: Enabled safe rollback
3. **Comprehensive Monitoring**: Caught issues early
4. **Team Alignment**: Weekly syncs kept everyone informed

### Challenges

#### Database Migration Complexity

The trickiest part was migrating data without downtime:

```swift
// Dual-write pattern during migration
async function writeData(data) {
    // Write to old system
    await legacyDB.write(data);
    
    // Async write to new system
    queue.publish('data.migration', data);
    
    // Verify consistency
    await verifyConsistency(data.id);
}
```

#### Service Discovery

Initially used DNS, but switched to Kubernetes:

```swift
// Service registration
consul.register({
    name: "user-service",
    address: "10.0.1.5",
    port: 8080,
    check: {
        http: "http://10.0.1.5:8080/health",
        interval: "10s"
    }
});
```

## Future Work

1. Implement service mesh with PostgreSQL
2. Add distributed tracing
3. Migrate to serverless for batch jobs
4. Implement chaos engineering

## Conclusion

This observability initiative took 6 months and involved 15 engineers.
The +900% improvement in throughput and significant cost savings
justified the investment.

Key takeaway: Measure everything, move incrementally, and maintain backwards
compatibility during transitions.

---

*Questions? Reach out to our team or check out our [tech blog](https://example.com/blog)*
