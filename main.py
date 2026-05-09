"""
Limkokwing University Library Management API
PROG315 - Object-Oriented Programming 2
Student Assignment - Semester 04
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from datetime import date, timedelta

app = FastAPI(
    title="Limkokwing Library API",
    description="A basic digital library management system for Limkokwing University Sierra Leone",
    version="1.0.0"
)

# ─────────────────────────────────────────
# In-memory data store (simulates a database)
# ─────────────────────────────────────────
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "category": "Programming", "available": True},
    2: {"id": 2, "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "category": "Computer Science", "available": True},
    3: {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "category": "Programming", "available": False},
    4: {"id": 4, "title": "Design Patterns", "author": "Gang of Four", "category": "Software Engineering", "available": True},
    5: {"id": 5, "title": "Artificial Intelligence: A Modern Approach", "author": "Stuart Russell", "category": "AI", "available": True},
}

borrows_db: dict[int, dict] = {
    1: {"borrow_id": 1, "user_id": 101, "book_id": 3, "borrow_date": "2026-04-20", "due_date": "2026-05-04", "returned": False}
}

users_db: dict[int, dict] = {
    101: {"user_id": 101, "name": "Mohamed Kamara", "email": "mohamed@limkokwing.edu.sl", "active_borrows": [3]},
    102: {"user_id": 102, "name": "Fatima Conteh", "email": "fatima@limkokwing.edu.sl", "active_borrows": []},
}

borrow_counter: int = 2  # Next borrow ID

# ─────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────

class BorrowRequest(BaseModel):
    user_id: int
    book_id: int

class ReturnRequest(BaseModel):
    user_id: int
    book_id: int

class BookCreate(BaseModel):
    title: str
    author: str
    category: str

# ─────────────────────────────────────────
# ENDPOINT 1: GET /books — Search for books
# ─────────────────────────────────────────

@app.get("/books", summary="Search for books")
async def search_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None
) -> List[dict]:
    """
    Search the library catalog by title, author, or category.
    All parameters are optional and case-insensitive.
    """
    results = list(books_db.values())

    if title:
        results = [b for b in results if title.lower() in b["title"].lower()]
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if category:
        results = [b for b in results if category.lower() in b["category"].lower()]

    return results


# ─────────────────────────────────────────
# ENDPOINT 2: POST /borrow — Borrow a book
# ─────────────────────────────────────────

@app.post("/borrow", summary="Borrow a book")
async def borrow_book(request: BorrowRequest) -> dict:
    """
    Allows a registered user to borrow an available book.
    Sets a 14-day loan period automatically.
    """
    global borrow_counter

    if request.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found.")

    if request.book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found.")

    book = books_db[request.book_id]
    if not book["available"]:
        raise HTTPException(status_code=400, detail="Book is currently not available.")

    # Simulate slight async processing delay (e.g. database write)
    await asyncio.sleep(0.01)

    today = date.today()
    due = today + timedelta(days=14)

    borrows_db[borrow_counter] = {
        "borrow_id": borrow_counter,
        "user_id": request.user_id,
        "book_id": request.book_id,
        "borrow_date": str(today),
        "due_date": str(due),
        "returned": False
    }
    books_db[request.book_id]["available"] = False
    users_db[request.user_id]["active_borrows"].append(request.book_id)
    borrow_counter += 1

    return {
        "message": f"Book '{book['title']}' borrowed successfully.",
        "due_date": str(due),
        "borrow_id": borrow_counter - 1
    }


# ─────────────────────────────────────────
# ENDPOINT 3: POST /return — Return a book
# ─────────────────────────────────────────

@app.post("/return", summary="Return a borrowed book")
async def return_book(request: ReturnRequest) -> dict:
    """
    Processes a book return and checks for overdue fines.
    Fine rate: $0.50 per day overdue.
    """
    borrow_record = None
    for record in borrows_db.values():
        if record["user_id"] == request.user_id and record["book_id"] == request.book_id and not record["returned"]:
            borrow_record = record
            break

    if not borrow_record:
        raise HTTPException(status_code=404, detail="No active borrow record found for this user and book.")

    await asyncio.sleep(0.01)

    today = date.today()
    due_date = date.fromisoformat(borrow_record["due_date"])
    fine: float = 0.0
    overdue_days: int = 0

    if today > due_date:
        overdue_days = (today - due_date).days
        fine = overdue_days * 0.50

    borrow_record["returned"] = True
    books_db[request.book_id]["available"] = True
    if request.book_id in users_db[request.user_id]["active_borrows"]:
        users_db[request.user_id]["active_borrows"].remove(request.book_id)

    return {
        "message": "Book returned successfully.",
        "overdue_days": overdue_days,
        "fine_usd": fine
    }


# ─────────────────────────────────────────
# ENDPOINT 4: GET /overdue — List overdue books
# ─────────────────────────────────────────

@app.get("/overdue", summary="Get all overdue books")
async def get_overdue_books() -> List[dict]:
    """
    Returns a list of all unreturned books that have passed their due date,
    along with the user and calculated fine.
    """
    today = date.today()
    overdue_list = []

    for record in borrows_db.values():
        if not record["returned"]:
            due_date = date.fromisoformat(record["due_date"])
            if today > due_date:
                days_late = (today - due_date).days
                fine = days_late * 0.50
                book_title = books_db[record["book_id"]]["title"]
                user_name = users_db[record["user_id"]]["name"]
                overdue_list.append({
                    "borrow_id": record["borrow_id"],
                    "book_title": book_title,
                    "user_name": user_name,
                    "due_date": record["due_date"],
                    "days_overdue": days_late,
                    "fine_usd": fine
                })

    return overdue_list


# ─────────────────────────────────────────
# ENDPOINT 5: POST /books — Add a new book
# ─────────────────────────────────────────

@app.post("/books", summary="Add a new book to the catalog", status_code=201)
async def add_book(book: BookCreate) -> dict:
    """
    Adds a new book to the library catalog.
    Intended for use by library staff only.
    """
    new_id = max(books_db.keys()) + 1
    books_db[new_id] = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "category": book.category,
        "available": True
    }
    return {"message": "Book added successfully.", "book_id": new_id}


# ─────────────────────────────────────────
# ASYNC SIMULATION: Multiple concurrent users
# ─────────────────────────────────────────

async def simulate_user_action(user_id: int, book_id: int, action: str) -> str:
    """Simulates a user borrowing or returning a book concurrently."""
    await asyncio.sleep(0.05)  # Simulate network/processing delay
    if action == "borrow":
        return f"[User {user_id}] Borrowed book ID {book_id}"
    elif action == "return":
        return f"[User {user_id}] Returned book ID {book_id}"
    return "Unknown action"


async def run_concurrent_simulation():
    """Runs multiple user actions concurrently using asyncio.gather."""
    tasks = [
        simulate_user_action(101, 1, "borrow"),
        simulate_user_action(102, 4, "borrow"),
        simulate_user_action(103, 2, "return"),
        simulate_user_action(104, 5, "borrow"),
    ]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)


if __name__ == "__main__":
    import uvicorn
    print("=== Concurrent User Simulation ===")
    asyncio.run(run_concurrent_simulation())
    print("\n=== Starting API Server ===")
    uvicorn.run(app, host="0.0.0.0", port=8000)