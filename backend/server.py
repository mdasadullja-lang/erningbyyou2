from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3, os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    initData TEXT PRIMARY KEY,
                    clicks INTEGER DEFAULT 0,
                    balance REAL DEFAULT 0.0
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS withdraws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    initData TEXT,
                    method TEXT,
                    account TEXT,
                    amount REAL
                )""")
    conn.commit()
    conn.close()

init_db()

class CreditPayload(BaseModel):
    initData: str

class WithdrawPayload(BaseModel):
    initData: str
    method: str
    account: str

@app.get("/api/me")
def get_me(initData: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT clicks, balance FROM users WHERE initData=?", (initData,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (initData, clicks, balance) VALUES (?,0,0)", (initData,))
        conn.commit()
        clicks, balance = 0, 0.0
    else:
        clicks, balance = row
    conn.close()
    return {"clicks": clicks, "balance": balance}

@app.post("/api/credit")
def credit(payload: CreditPayload):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT clicks, balance FROM users WHERE initData=?", (payload.initData,))
    row = c.fetchone()
    if not row:
        clicks, balance = 0, 0.0
    else:
        clicks, balance = row
    clicks += 1
    balance = round(balance + 0.001, 3)
    c.execute("REPLACE INTO users (initData, clicks, balance) VALUES (?,?,?)",
              (payload.initData, clicks, balance))
    conn.commit()
    conn.close()
    return {"clicks": clicks, "balance": balance}

@app.post("/api/withdraw")
def withdraw(payload: WithdrawPayload):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE initData=?", (payload.initData,))
    row = c.fetchone()
    if not row or row[0] < 2.0:
        conn.close()
        return {"error": "Minimum withdraw not reached"}
    balance = row[0]
    c.execute("INSERT INTO withdraws (initData, method, account, amount) VALUES (?,?,?,?)",
              (payload.initData, payload.method, payload.account, balance))
    c.execute("UPDATE users SET balance=0 WHERE initData=?", (payload.initData,))
    conn.commit()
    withdraw_id = c.lastrowid
    conn.close()
    return {"status": "ok", "id": withdraw_id, "amount": balance, "method": payload.method, "account": payload.account}

@app.get("/api/admin/withdraws")
def get_withdraws():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM withdraws ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "initData": r[1], "method": r[2], "account": r[3], "amount": r[4]} for r in rows]

@app.get("/admin/withdraws", response_class=HTMLResponse)
def withdraws_page(request: Request):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM withdraws ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return templates.TemplateResponse("withdraws.html", {"request": request, "withdraws": rows})
