# Django eLearning System

![CI](https://github.com/bambina/django-elearning-system/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/bambina/django-elearning-system/branch/main/graph/badge.svg)](https://codecov.io/gh/bambina/django-elearning-system)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Redis](https://img.shields.io/badge/Redis-7.2-red)
![Celery](https://img.shields.io/badge/Celery-5.3-orange)

## Overview

This project is a virtual eLearning System built with the Django framework.

The system consists of three main components:
- Admin: http://127.0.0.1:8000/admin/
- API (Swagger UI): http://127.0.0.1:8000/
- App (Top Page): http://127.0.0.1:8000/top

The application supports multiple user roles with different permissions: **Admin**, **Teacher**, and **Student**.

## Tech Stack
- Backend Framework: `Django`, `Django REST Framework`
- Asynchronous Task Queue: `Celery` (with Redis as broker)
- Real-Time Communication: `Django Channels` (WebSocket, backed by Redis)
- Database: SQLite (for prototyping; replaceable with PostgreSQL, MySQL, etc.)
- Testing: pytest

## Key Features

- **Asynchronous Task Processing with Celery and Redis**  
  Notifications are delivered in the background using Celery (worker) with Redis (broker).
  This ensures that time-consuming fan-out operations, such as sending notifications to all enrolled students, do not block the main Django application, improving responsiveness and scalability.

- **Real-Time Chat with Django Channels and Redis**  
  Teachers can start a Live Q&A Session where students and teachers interact through real-time chat.
  When a session begins, notifications are dispatched only to enrolled students, and access is restricted to course participants.
  The main implementation resides in `QASessionConsumer` (server-side) and `active_qa_session.js` (client-side).

## Setup

### Requirements

- Python 3.12 (tested on 3.12.2)
- SQLite 3.43+
- Redis 7.2 (tested on 7.2.5)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Running

```bash
# Start Redis (in a separate terminal)
redis-server --port 6379

# Start Celery worker (in another terminal)
celery --app=elearning.celery:app worker --loglevel=INFO

# Database
python manage.py migrate
python manage.py populate_database

# Start Django server
python manage.py runserver 127.0.0.1:8000

# Demo accounts (for testing)
# Admin   -> admin / abc
# Teacher -> teacher1 / abc
# Student -> student1 / abc
```

### Testing

```bash
# Before running tests, make sure Redis and Celery worker are running.
pytest userportal/tests --cov
```
