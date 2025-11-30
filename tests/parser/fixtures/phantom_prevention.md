# Phantom Block Prevention Test

This document tests scenarios that could create phantom blocks.

```python
print("legitimate block 1")
```
```python
print("legitimate block 2")
```

The above blocks are adjacent and should not be considered phantom blocks.

```bash
echo "block 3"
```

```
# Empty language block
echo "block 4"
```

End of test.