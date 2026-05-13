# OOP-2
PROG315 – Object-Oriented Programming 2 | Semester 04 | March – July 2026*
Limkokwing University of Creative Technology, Sierra Leone

---

## Description

A RESTful API built with *Python FastAPI* for managing the Limkokwing University library system. It allows students to search for books, borrow and return them, and enables staff to track overdue loans and fines. The system uses asynchronous programming to support multiple users at the same time.

---

## Features

- Search books by title, author, or category
- Borrow books with automatic 14-day due date
- Return books with overdue fine calculation ($0.50/day)
- View all overdue books and fines (staff)
- Add new books to the catalog (staff)
- Async/await support for concurrent user requests

---

## Tech Stack

- *Language:* Python 3.11+
- *Framework:* FastAPI
- *Validation:* Pydantic
- *Server:* Uvicorn
- *Async:* asyncio

---

## Setup & Installation

bash
# 1. Clone the repository
git clone https://github.com/PhilipSei/limkokwing-library-api.git
cd limkokwing-library-api

# 2. Install dependencies
pip install fastapi uvicorn

# 3. Run the server
python main.py


Open *http://localhost:8000/docs* in your browser to access the interactive Swagger UI.

---

## API Endpoints

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| GET    | /books     | Search books by title/author/category |
| POST   | /borrow    | Borrow a book                      |
| POST   | /return    | Return a book                      |
| GET    | /overdue   | List all overdue books with fines  |
| POST   | /books     | Add a new book to the catalog      |

---

## Example Requests

*Search for a book:*

GET /books?category=Programming


*Borrow a book:*
json
POST /borrow
{
  "user_id": 101,
  "book_id": 2
}


*Return a book:*
json
POST /return
{
  "user_id": 101,
  "book_id": 2
}


---

## Project Structure


limkokwing-library-api/
├── main.py          # Full FastAPI source code
├── README.md        # Project documentation
├── .gitignore       # Excludes cache and env files
└── requirements.txt # Python dependencies
