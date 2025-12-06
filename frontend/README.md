# Sport Complex Frontend

Vue 3 + Vite frontend for the Sport Complex management system.

## Features

- Vue 3 with Composition API
- Tailwind CSS for styling
- Dark mode support with theme toggle
- Responsive design
- GitHub-like UI with left sidebar navigation
- Role-based access control (Client, Trainer, Admin)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

To build for production:
```bash
npm run build
```

## Configuration

The frontend is configured to proxy API requests to `http://127.0.0.1:8000` (the FastAPI backend). This is configured in `vite.config.js`.

Make sure your FastAPI backend is running on port 8000 before starting the frontend.

### CORS Configuration (for production)

If you plan to deploy the frontend separately from the backend, you'll need to enable CORS in your FastAPI backend. Add the following to your `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Project Structure

```
frontend/
├── src/
│   ├── views/          # Page components
│   ├── layouts/        # Layout components
│   ├── services/       # API services
│   ├── router/         # Vue Router configuration
│   ├── composables/    # Vue composables (theme, etc.)
│   └── App.vue         # Root component
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Theme

- Main color: White
- Accent color: Blue (#0066CC)
- Dark mode: Toggle available in footer

