# Debugging Data Corruption in Node.js Application

## Symptoms

- incorrect data in database
- Eventually leads to system failure
- Occurs under high load conditions

## Environment

- Node.js version: latest
- OS: Linux
- Load: 1000+ requests/second

## Code Under Investigation

```javascript
// Main application code
function processRequest(req) {
    const data = fetchData(req.id);
    const result = transformData(data);
    cache[req.id] = result;  // Potential issue here
    return result;
}
```

## Diagnostic Output

```
Memory Usage Timeline:
T+0min:  512MB
T+10min: 1.2GB
T+20min: 2.5GB
T+30min: 4.1GB (OOM kill)
```

## Heap Analysis

```
Top Memory Consumers:
Object Type      | Count  | Size
-----------------|--------|--------
CachedData       | 50000  | 2.1GB
RequestContext   | 30000  | 800MB
ConnectionPool   | 500    | 50MB
```

## Root Cause

The cache grows unbounded because there's no eviction policy.

## Solution

Implemented LRU cache with size limits:

```javascript
// Fixed implementation
const LRU = require('lru-cache');
const cache = new LRU({
    max: 1000,
    maxAge: 1000 * 60 * 5  // 5 minutes
});

function processRequest(req) {
    const data = fetchData(req.id);
    const result = transformData(data);
    cache.set(req.id, result);
    return result;
}
```

## Verification

After fix:
- Memory stable at ~600MB
- No OOM kills in 7 days
- Performance improved 20%

## Lessons

1. Always set limits on caches
2. Monitor memory usage
3. Use profiling tools early
4. Test under realistic load
