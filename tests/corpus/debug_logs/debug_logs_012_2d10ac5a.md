# Debugging Authentication Failure in Vault (Scala)

**Session ID:** DEBUG-7CBAAA5C4BD7  
**Date:** 2025-12-06 01:35:53  
**Severity:** High  
**Status:** Resolved

## Problem Statement

Production Vault cluster experiencing authentication failure resulting in:
- System Instability
- Service degradation
- Impact to 25% of users

## Environment

```yaml
environment: production
cluster: vault-prod-us-east-1
version: v2.7.17
instances: 6
load: 31240 req/min
```

## Timeline

| Time | Event |
|------|-------|
| 14:30 | First alert: High memory usage |
| 14:35 | CPU usage spiking to 90% |
| 14:42 | Started investigation |
| 15:10 | Root cause identified |
| 15:30 | Fix deployed to canary |
| 16:00 | Full rollout completed |

## Investigation

### Step 1: Metrics Analysis

```python
# Query Prometheus for memory trends
import prometheus_client as prom

query = '''
  rate(process_resident_memory_bytes{job="vault"}[5m])
'''

results = prom.query(query, time.now() - 3600)
for metric in results:
    print(f"Instance: {metric['instance']}")
    print(f"Memory growth: {metric['value']} bytes/sec")
```

Output revealed memory growth of 10MB/min on all instances.

### Step 2: Heap Dump Analysis

```bash
# Capture heap dump
jmap -dump:format=b,file=heap.bin <pid>

# Analyze with MAT
mat -analyze heap.bin
```

Top memory consumers:

| Class | Instances | Size |
|-------|-----------|------|
| ScalaHashMap | 1,500,000 | 120 MB |
| ScalaString | 3,000,000 | 90 MB |
| CustomCache | 500,000 | 180 MB |

### Step 3: Code Review

Located problematic code:

```scala
// BEFORE: Leaking implementation
class DataProcessor {
    private Map<String, Data> cache = new HashMap<>();
    
    public Data process(String id) {
        // Cache never cleared!
        if (!cache.containsKey(id)) {
            Data data = fetchFromDB(id);
            cache.put(id, data);  // MEMORY LEAK
        }
        return cache.get(id);
    }
}
```

### Step 4: Profiling

```scala
// Enable profiling
Profiler profiler = new AsyncProfiler();
profiler.start("cpu,alloc");

// Run workload
for (int i = 0; i < 10000; i++) {
    processor.process("key-" + i);
}

profiler.stop();
profiler.dumpFlameGraph("profile.html");
```

Flamegraph revealed:
- 85% time in `HashMap.put()`
- 60% allocations in `Data` objects
- No cache eviction occurring

## Root Cause

Configuration Issue in Vault Scala application. Cache size grew unbounded
because there was no eviction policy implemented.

## Solution

### Implement LRU Cache

```scala
// AFTER: Fixed with LRU cache
import com.google.common.cache.CacheBuilder;

class DataProcessor {
    private LoadingCache<String, Data> cache = CacheBuilder
        .newBuilder()
        .maximumSize(10_000)  // Limit size
        .expireAfterWrite(5, TimeUnit.MINUTES)  // TTL
        .recordStats()  // Enable metrics
        .build(new CacheLoader<String, Data>() {
            public Data load(String id) {
                return fetchFromDB(id);
            }
        });
    
    public Data process(String id) {
        return cache.get(id);
    }
}
```

### Add Monitoring

```scala
// Export cache metrics
import io.prometheus.client.Gauge;

Gauge cacheSize = Gauge.build()
    .name("cache_size")
    .help("Current cache size")
    .register();

Gauge cacheHitRate = Gauge.build()
    .name("cache_hit_rate")
    .help("Cache hit rate")
    .register();

// Update periodically
executor.scheduleAtFixedRate(() -> {
    CacheStats stats = cache.stats();
    cacheSize.set(cache.size());
    cacheHitRate.set(stats.hitRate());
}, 0, 10, TimeUnit.SECONDS);
```

## Verification

### Before Fix

```
Memory Usage:
T+0:   500 MB
T+10:  800 MB
T+20:  1.2 GB
T+30:  1.8 GB (restart required)

Cache Hit Rate: 45%
Response Time p95: 850ms
```

### After Fix

```
Memory Usage:
T+0:   500 MB
T+10:  520 MB
T+20:  530 MB
T+30:  525 MB (stable)

Cache Hit Rate: 82%
Response Time p95: 120ms
```

## Lessons Learned

1. **Always implement cache eviction policies**
   - Size limits
   - TTL/expiration
   - LRU/LFU strategies

2. **Monitor cache metrics**
   - Hit/miss rates
   - Size growth
   - Eviction counts

3. **Load test thoroughly**
   - Simulate production traffic
   - Monitor for memory growth
   - Test cache behavior under load

4. **Use profiling tools proactively**
   - Regular heap dump analysis
   - CPU/allocation profiling
   - Memory leak detection

## Related Incidents

- Similar issue in Payment Service (2024-03-15)
- Cache overflow in Auth Service (2024-04-22)

## Action Items

- [ ] Add cache size alerts (threshold: 80% of max)
- [ ] Document caching best practices
- [ ] Review all caching code for similar issues
- [ ] Add cache metrics to dashboards

---

**Resolution Time:** 1.5 hours  
**Root Cause Category:** Code defect  
**Prevention:** Code review + monitoring
