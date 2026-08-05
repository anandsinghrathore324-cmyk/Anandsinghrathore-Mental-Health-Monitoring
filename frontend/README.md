# AIRA Frontend Client

The frontend of **AIRA (AI-Powered Mental Health & Support Platform)** is a lightweight, responsive client application built with semantic HTML5, CSS3 neon cyberpunk styling, and modular Vanilla JavaScript.

---

## 📁 Directory Layout

```
frontend/
├── index.html            # Main dashboard, self-assessment, AI chatbot & risk analytics
├── doctor-support.html   # Professional therapist directory with geospatial search
├── features.html         # Interactive wellness tools (Breathing, Journal, SOS, White Noise)
├── script.js             # Client state orchestration, particle canvas & Chart.js graphs
├── style.css             # Unified dark cyberpunk design system & responsive layout
└── package.json          # Development server scripts
```

---

## 🚀 Running the Frontend Locally

From the `frontend/` directory:
```bash
npm run dev
# Starts http-server on http://localhost:3000
```

Or from the project root:
```bash
npm run dev:frontend
```

---

## 🔌 API Connection

The frontend connects to the backend API (`http://127.0.0.1:5001/api` by default). In production, `API_BASE_URL` in `script.js` dynamically adapts to the current origin or configured environment endpoint.
