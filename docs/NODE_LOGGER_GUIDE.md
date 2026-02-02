# Node Script Development Guide: Using the Logger

This guide explains how to use the Loom logging system in your custom node scripts.

## Table of Contents

- [Quick Start](#quick-start)
- [Function Reference](#function-reference)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Quick Start

### Import the Logger

Add this import at the top of your node script:

```python
from executor.utils.node_logger import log_print, log_warning, log_error
```

### Use in Your Code

```python
def my_node_function(input1, input2):
    log_print("Starting calculation...")
    
    result = input1 + input2
    
    log_print(f"Calculation complete: {result}")
    
    return result
```

That's it! Your logs will appear in the Properties Bar when the engine runs.

---

## Function Reference

### `log_print(message, level="info")`

**Main logging function** - Use this for all regular logs.

**Parameters:**
- `message` (str): The message to log
- `level` (str, optional): Log level - "info", "warning", or "error". Default is "info"

**Example:**
```python
log_print("Processing data...")
log_print("Found 10 items")
log_print("Operation successful!")
```

---

### `log_warning(message)`

**Convenience function** for warnings.

**Parameters:**
- `message` (str): The warning message

**Example:**
```python
if value < 0:
    log_warning("Negative value detected, using absolute value")
    value = abs(value)
```

---

### `log_error(message)`

**Convenience function** for errors.

**Parameters:**
- `message` (str): The error message

**Example:**
```python
try:
    result = risky_operation()
except Exception as e:
    log_error(f"Operation failed: {str(e)}")
    return None
```

---

## Best Practices

### ✅ DO:

1. **Log important milestones**
   ```python
   log_print("Loading data from file...")
   data = load_data()
   log_print(f"Loaded {len(data)} records")
   ```

2. **Log warnings for recoverable issues**
   ```python
   if config is None:
       log_warning("No config found, using defaults")
       config = get_defaults()
   ```

3. **Log errors for failures**
   ```python
   if not validate(input):
       log_error("Invalid input format")
       return None
   ```

4. **Include context in messages**
   ```python
   log_print(f"Processing {filename} with {num_records} records")
   ```

### ❌ DON'T:

1. **Don't spam logs**
   ```python
   # BAD: Inside a loop
   for i in range(10000):
       log_print(f"Processing item {i}")  # Too many logs!
   ```

2. **Don't log sensitive data**
   ```python
   # BAD: Exposing passwords/keys
   log_print(f"API Key: {api_key}")  # Security risk!
   ```

3. **Don't use print() for user messages**
   ```python
   # BAD: Using print
   print("Processing...")  # User won't see this!
   
   # GOOD: Using log_print
   log_print("Processing...")  # User sees this in UI
   ```

---

## Examples

### Example 1: Basic Math Node

```python
from executor.utils.node_logger import log_print

def add_numbers(a, b):
    """Add two numbers and log the operation"""
    log_print(f"Adding {a} + {b}")
    
    result = a + b
    
    log_print(f"Result: {result}")
    
    return result
```

### Example 2: File Processing Node

```python
from executor.utils.node_logger import log_print, log_warning, log_error
import os

def process_file(file_path):
    """Process a file and log progress"""
    
    if not os.path.exists(file_path):
        log_error(f"File not found: {file_path}")
        return None
    
    log_print(f"Opening file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        log_print(f"Read {len(lines)} lines from file")
        
        if len(lines) == 0:
            log_warning("File is empty!")
        
        return content
        
    except Exception as e:
        log_error(f"Failed to read file: {str(e)}")
        return None
```

### Example 3: Data Validation Node

```python
from executor.utils.node_logger import log_print, log_warning, log_error

def validate_data(data, min_value, max_value):
    """Validate data is within range"""
    
    log_print(f"Validating data: range [{min_value}, {max_value}]")
    
    if data is None:
        log_error("Data is None")
        return False
    
    if data < min_value:
        log_warning(f"Data {data} is below minimum {min_value}")
        return False
    
    if data > max_value:
        log_warning(f"Data {data} exceeds maximum {max_value}")
        return False
    
    log_print("✓ Data validation passed")
    return True
```

### Example 4: Loop with Progress Updates

```python
from executor.utils.node_logger import log_print

def process_batch(items):
    """Process items in batches with progress updates"""
    
    total = len(items)
    log_print(f"Starting batch processing: {total} items")
    
    results = []
    batch_size = 100
    
    for i in range(0, total, batch_size):
        batch = items[i:i+batch_size]
        
        # Log every 100 items instead of every item
        processed = i + len(batch)
        log_print(f"Progress: {processed}/{total} items processed")
        
        results.extend([process_item(item) for item in batch])
    
    log_print("✓ Batch processing complete")
    return results
```

---

## Understanding Log Levels

Logs are displayed in the Properties Bar with different colors based on level:

- **Info** (default): Green background - normal operation logs
- **Warning**: Yellow/amber background - issues that don't stop execution
- **Error**: Red/rose background - failures and critical issues

---

## Technical Notes

### How It Works

1. `log_print()` writes to a JSON file in your project folder
2. The frontend polls this file when the engine is running
3. Logs appear in real-time in the Properties Bar
4. Logs are cleared when you start a new execution

### Performance

- Logging is very fast (file I/O only)
- No network overhead
- Safe to call multiple times per node
- **But**: Don't spam logs in tight loops!

### When to Use print() vs log_print()

| Use Case | Function | Why |
|----------|----------|-----|
| User-facing messages | `log_print()` | Shows in UI |
| Debug output (development) | `print()` | Shows in terminal |
| Critical errors | `log_error()` | Shows in UI with red color |
| Warnings | `log_warning()` | Shows in UI with yellow color |

---

## Common Patterns

### Pattern: Try-Catch with Logging

```python
def safe_operation(input_data):
    try:
        log_print("Starting operation...")
        result = risky_function(input_data)
        log_print("Operation successful")
        return result
    except ValueError as e:
        log_error(f"Invalid value: {e}")
        return None
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return None
```

### Pattern: Conditional Logging

```python
def process_with_verbose(data, verbose=True):
    if verbose:
        log_print(f"Processing {len(data)} items")
    
    result = process(data)
    
    if verbose:
        log_print("Processing complete")
    
    return result
```

### Pattern: Progress Percentage

```python
def long_operation(items):
    total = len(items)
    log_print(f"Starting operation on {total} items")
    
    for i, item in enumerate(items):
        process(item)
        
        # Log every 10%
        if (i + 1) % (total // 10) == 0:
            percent = ((i + 1) / total) * 100
            log_print(f"Progress: {percent:.0f}%")
    
    log_print("Operation complete!")
```

---

## FAQ

**Q: Will logging slow down my node?**  
A: No. Logging is very fast (simple file write). Just don't log inside tight loops.

**Q: Can I use f-strings in logs?**  
A: Yes! f-strings are the recommended way to format log messages.

**Q: What if I forget to import the logger?**  
A: Your node will work fine, you just won't see logs in the UI.

**Q: Can I log objects or dictionaries?**  
A: Convert them to strings first: `log_print(f"Data: {str(my_dict)}")`

**Q: Are logs saved after execution?**  
A: Logs are cleared when you start a new execution. They're meant for monitoring, not archiving.

---

## Summary

1. **Import**: `from executor.utils.node_logger import log_print`
2. **Use**: `log_print("Your message here")`  
3. **View**: Logs appear in Properties Bar (when nothing is selected)
4. **Remember**: Be concise, avoid loops, include context!

Happy logging! 🎯
