# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Utawakufinder is a karaoke video parsing service that extracts song timestamps from YouTube livestream comments and organizes them into a searchable interface. The project processes YouTube video URLs to extract song information (title, artist, timestamp) from comments and presents them in a YouTube-like interface with filtering capabilities.

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js + TailwindCSS + TypeScript
- **Data Storage**: JSON files for song metadata
- **External APIs**: YouTube Data API v3

## Development Commands

### Docker Development (Recommended)
```bash
# Run entire application stack
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Manual Development Setup

#### Backend (Port 9030)
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI development server
uvicorn main:app --reload --port 9030
```

#### Frontend (Port 3030)
```bash
cd frontend

# Install dependencies
npm install

# Run Next.js development server
npm run dev
```

### Testing YouTube Data Extraction
```bash
# Test via API endpoints
curl -X POST "http://localhost:9030/parse-video" \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUTUBE_URL_HERE"}'
```

## Code Architecture

### Core Components

**crawler.py** - YouTube data extraction module:
- `extract_video_id()` - Extracts video IDs from YouTube URLs
- `find_comment()` - Fetches comments using YouTube API with pagination

**main.py** - FastAPI application with API endpoints:
- `parse_songs_from_comments()` - Parses timestamps directly from comments in memory
- REST API endpoints for video parsing, saving, and retrieval

### Data Flow
1. YouTube URL input → `extract_video_id()`
2. Video ID → `find_comment()` → fetch all comments with pagination
3. Comments → `parse_songs_from_comments()` → extract structured song data directly from memory
4. Song data → JSON storage for frontend consumption

### Comment Parsing Format
The system expects comments in the format: `HH:MM:SS | Song Title | Artist Name`
- Removes content within parentheses from titles and artist names
- Handles multi-page comment fetching (max 20 pages, 100 comments per page)

## Configuration Notes

- YouTube API key is hardcoded in crawler files (should be moved to environment variables)
- Video data is stored in `/data/videos.json`
- The system processes Korean text (UTF-8 encoding required)
- FastAPI server runs on port 9030 with auto-reload for development

## Dependencies

Key Python packages from `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `requests` - HTTP client for YouTube API
- `pydantic` - Data validation

Use 'docker compose' insteads 'docker-compose'