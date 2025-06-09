from fastapi import FastAPI
from routers import tableau

app = FastAPI(title="Tableau Automation API")

app.include_router(tableau.router, prefix="/tableau", tags=["Tableau Operations"]) 