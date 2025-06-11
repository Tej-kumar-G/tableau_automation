from fastapi import FastAPI
from routers import tableau

app = FastAPI(title="Tableau Automation API")

app.include_router(tableau.router, prefix="/tableau", tags=["Tableau Operations"]) 


@app.on_event("startup")
def start_background_monitoring():
    thread = threading.Thread(target=run_monitoring)
    thread.start()