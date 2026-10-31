"""
VolGuard AI - FastAPI Server Entrypoint
Owned by Person 1 (Backend & Quantitative Modeling)

Serves:
  - `uvicorn main:app --port 8000 --reload`
  - `uvicorn api:app --port 8000 --reload`
"""
from api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
