# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PintxoPote is a Django web application for recording, searching, and sharing pintxo bar notes in San Sebastián. It's designed as a personal tool with public read-only sharing capabilities, controlled by admin token authentication.

## Development Commands

### Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database Management
```bash
python manage.py migrate
python manage.py makemigrations
```

### Development Server
```bash
export DJANGO_SETTINGS_MODULE=pintxopote.settings
python manage.py runserver
# App available at http://127.0.0.1:8000/
```

### Local Environment Variables
Create a `.env` file in the project root:
```
DJANGO_SECRET_KEY=anything-long-and-random
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_TOKEN=devadmintoken
```

## Architecture

### Tech Stack
- **Backend**: Django 5.0+ with SQLite database
- **Frontend**: HTMX + Tailwind CSS (no build process)
- **Media Storage**: Local filesystem (`/static/uploads`)
- **Authentication**: Admin token-based (via environment variable)
- **Deployment**: Railway with auto-deploy from main branch

### Key Components
- **Data Storage**: Dual-mode data directory handling
  - Local: `./data/` (created automatically)
  - Production (Railway): `/app/data` (persistent volume mount)
- **Media Handling**: Photos stored in `DATA_DIR/uploads` with automatic directory creation
- **Database**: SQLite at `DATA_DIR/db.sqlite3`

### Data Model (Planned MVP)
Core entity is a pintxo bar with fields including:
- Required: Name, Address, Notes
- Optional: Map Link, Specialties, Price Range, Caña Price, Crowd Level, Last Visited, Tags, Photos
- Auto-generated: UUID, Latitude/Longitude

### Application Structure
- Standard Django project layout with `pintxopote/` as main app directory
- Currently minimal setup - main views and models need to be implemented
- PWA capabilities planned (manifest.json + service worker)

### Deployment
- Railway auto-deploys on push to main branch
- Persistent volume mounted for database and media files
- Production environment detected via `RAILWAY_STATIC_URL` environment variable

## Development Guidelines

### Code Style
- Avoid over-engineered solutions
- Provide sufficient comments for variables, logic, and flow
- Follow Django best practices and conventions

### Features Priority (MVP)
1. Entry form with all fields
2. Search functionality (name search with live results)
3. Filtering (Caña price, tags, street, price range)
4. List view (home), detail view (bar), and add form
5. Quick Note and Quick Photo append actions
6. Public read-only sharing

### Authentication Model
- Edit rights controlled by `ADMIN_TOKEN` environment variable
- Public visitors have read-only access
- No user registration/login system planned for MVP

## Design System

### Spanish-Inspired Color Palette
When updating UI components, use these cohesive Tailwind classes:

**Primary Colors:**
- **Terracotta/Rust**: `bg-red-600`, `bg-red-700`, `bg-red-800` (buttons, headers, accents)
- **Warm Stone**: `bg-amber-100`, `bg-amber-200`, `bg-amber-300` (card backgrounds, subtle highlights)
- **Saffron**: `bg-yellow-500`, `bg-yellow-600` (call-to-action, highlights)

**Secondary Colors:**
- **Basque Green**: `bg-emerald-600`, `bg-emerald-700` (success states, secondary actions)
- **Mediterranean Blue**: `bg-blue-500`, `bg-blue-600` (links, info states)
- **Warm Cream**: `bg-amber-50`, `bg-amber-100` (page backgrounds, input fields)

**Neutral Colors:**
- **Charcoal**: `bg-gray-700`, `bg-gray-800`, `text-gray-800` (headers, primary text)
- **Warm Gray**: `text-gray-700`, `text-gray-600` (body text, secondary text)

### Typography Guidelines
- **Headers**: `font-bold text-gray-800` (warm, authoritative)
- **Body Text**: `text-gray-700` (readable, slightly warm)
- **Highlights**: `text-yellow-600` (saffron accents for emphasis)
- **Links**: `text-blue-600 hover:text-blue-800` (Mediterranean blue)

### Component Styling Patterns
- **Cards**: `bg-amber-50 shadow-md` (warm stone background)
- **Primary Buttons**: `bg-red-600 hover:bg-red-700 text-white` (terracotta)
- **Secondary Buttons**: `bg-emerald-600 hover:bg-emerald-700 text-white` (Basque green)
- **Tags/Badges**: `bg-amber-100 text-amber-800` (warm stone with darker text)
- **Success Messages**: `bg-emerald-100 border-emerald-400 text-emerald-700`
- **Form Inputs**: `bg-white border-gray-300 focus:ring-yellow-500` (saffron focus states)

### Spacing & Layout
- Use generous spacing (`space-y-6`, `p-6`) to create a relaxed, café-like atmosphere
- Cards should have rounded corners (`rounded-lg`) and subtle shadows (`shadow-md`)
- Maintain warm, inviting feeling throughout the interface