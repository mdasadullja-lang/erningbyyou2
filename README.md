# Telegram MiniApp with Monetag Ads + Withdraw System

## 📌 Features
- Telegram Mini App (frontend)
- Monetag Ads integration
- Reward system: earn $0.001 per ad click
- Withdraw available when balance ≥ $2
- Withdraw methods: bKash, Nagad, Bank
- Admin Panel to view withdraw requests

## 🚀 Project Structure
```
frontend/index.html     → User MiniApp (upload to Spaceship)
backend/server.py       → FastAPI backend
backend/templates/      → HTML templates (withdraw admin panel)
backend/requirements.txt → Dependencies
```

## ⚡ Deployment
1. **Frontend** → Upload `frontend/index.html` to Telegram Spaceship.
2. **Backend** → Deploy `backend/` folder on Render / Railway:
   ```bash
   pip install -r requirements.txt
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```
3. Replace `API_BASE` in `frontend/index.html` with your backend URL:
   ```js
   const API_BASE = "https://your-backend.onrender.com";
   ```

## 🔑 Admin Panel
Visit:
```
https://your-backend.onrender.com/admin/withdraws
```
to see withdraw requests in table format.
