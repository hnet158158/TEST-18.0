# FastAPI Sync Usage Specs

## Sync vs Async in FastAPI

FastAPI supports both `def` (synchronous) and `async def` (asynchronous) path operation functions.

### How it works internally:
- **`async def`**: FastAPI runs these directly in the main event loop. It assumes you are using non-blocking I/O (like `httpx.AsyncClient` or `motor`).
- **`def`**: FastAPI runs these in a **separate thread pool** (from `anyio`). This prevents blocking the main event loop while the synchronous code (like standard `sqlite3` or sync `SQLAlchemy`) is running.

### Recommendation for this project:
Since we are using **Sync SQLAlchemy** and **SQLite**, all path operations SHOULD be defined using regular `def` to leverage the thread pool and avoid blocking the event loop.

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    # This runs in a thread pool
    return db.query(Item).all()
```

### Key Constraints:
- DO NOT use `async def` if you are calling blocking sync code inside.
- DO NOT use `time.sleep()` in `async def`; use `await asyncio.sleep()`.
- In `def` functions, `time.sleep()` is acceptable as it runs in a separate thread.
