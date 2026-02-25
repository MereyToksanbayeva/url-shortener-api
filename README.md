# URL Shortener API (Flask)

A simple **URL shortener service** (bit.ly style) built with Flask + SQLite.

## Features
- Create a short URL from a long URL
- Redirect from short code to original URL
- Click tracking (view count)
- URL info endpoint

## Tech Stack
- Python
- Flask
- SQLAlchemy
- SQLite

## API

### Health
- `GET /health`

### Create short URL
- `POST /api/shorten`
Body:
```json
{ "url": "https://example.com" }
