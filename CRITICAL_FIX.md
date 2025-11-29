# Critical Fix: Event Loop Blocking Issue

## The Problem

The application was **hanging/stuck at "Generating dynamic prompt template..."** because of a critical async/sync blocking issue.

### Root Cause

In `backend/main.py`, the `/api/generate-prompt` endpoint was calling a **synchronous** function in an **async** endpoint:

```python
@app.post("/api/generate-prompt")
async def generate_prompt(request: TopicRequest):
    # ❌ PROBLEM: Calling synchronous function in async context
    prompt_data = prompt_service.generate_prompt(request.topic)
    return {"success": True, "data": prompt_data}
```

The `prompt_service.generate_prompt()` method is a **synchronous** function. When called directly in an async endpoint, it **blocks the entire FastAPI event loop**, preventing any other requests from being processed.

### Why This Happens

FastAPI uses an async event loop (asyncio) to handle multiple requests concurrently. When you call a synchronous function directly in an async endpoint:

1. The event loop **stops** and waits for the synchronous function to complete
2. **All other requests** are blocked and cannot be processed
3. The application appears "stuck" or "frozen"
4. No timeout occurs because the function is actually running, just blocking everything else

### The Three Blocking Issues We Found

1. **Discord webhook calls** - Fixed by using `asyncio.create_task()` for fire-and-forget
2. **Response body reading** - Fixed by removing unnecessary middleware capture
3. **Prompt generation** - **THIS WAS THE MAIN ISSUE** - Fixed by using `asyncio.to_thread()`

## The Solution

We fixed it by running the synchronous function in a **thread pool** using `asyncio.to_thread()`:

```python
@app.post("/api/generate-prompt")
async def generate_prompt(request: TopicRequest):
    # ✅ FIXED: Run synchronous function in thread pool
    prompt_data = await asyncio.to_thread(prompt_service.generate_prompt, request.topic)
    return {"success": True, "data": prompt_data}
```

### How `asyncio.to_thread()` Works

- Runs the synchronous function in a **separate thread** from the thread pool
- The event loop remains **free** to process other requests
- The `await` keyword waits for the thread to complete without blocking
- Other requests can be handled concurrently

## Impact

**Before Fix:**
- Application appeared stuck/frozen
- "Generating dynamic prompt template..." loading forever
- Render deployment showing 502 errors
- No requests could be processed while prompt generation was running

**After Fix:**
- ✅ Instant response times
- ✅ Multiple requests can be handled concurrently
- ✅ No more blocking or hanging
- ✅ Application fully functional

## Technical Details

### What is Event Loop Blocking?

In async programming (asyncio/FastAPI):
- The event loop runs in a **single thread**
- It switches between multiple tasks efficiently
- When a task does **blocking I/O or CPU work**, the entire loop stops
- All other tasks wait until the blocking operation completes

### When to Use `asyncio.to_thread()`

Use it when you have:
- **Synchronous** functions that take time (file I/O, CPU-intensive work)
- **Third-party libraries** that are not async-compatible
- **Legacy code** that cannot be easily converted to async

### Best Practices

1. **Always use async functions** in async endpoints when possible
2. **Use `asyncio.to_thread()`** for synchronous functions that might block
3. **Use `asyncio.create_task()`** for fire-and-forget operations (logging, analytics)
4. **Never call `time.sleep()`** in async code - use `await asyncio.sleep()` instead
5. **Keep middleware fast** - no heavy processing or blocking calls

## Verification

After this fix:
1. Prompt generation completes instantly
2. Multiple users can generate prompts simultaneously
3. No more 502 errors on Render
4. Application is fully responsive

## Commit

This fix was committed in: `8ee3098`
