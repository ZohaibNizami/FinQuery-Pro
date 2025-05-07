
from fastapi import FastAPI

from backend.app.health import health_router
from backend.app.db_status import db_router
from backend.app.routers import stocks
from backend.app.models import Base
from backend.app.database import engine

from backend.app.routers import fundamentals
from backend.app.routers import filings
from backend.app.routers import nlq
from backend.app.routers import insider
from backend.app.routers import analysts
from backend.app.routers import developments
from backend.app.routers import analytics

# Create the tables in the database
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(health_router)

app.include_router(db_router)

app.include_router(stocks.router, prefix="/api/v1", tags=["stocks"])

app.include_router(fundamentals.router, prefix="/api/v1", tags=["fundamentals"])

app.include_router(filings.router, prefix="/api/v1", tags=["filings"])

app.include_router(nlq.router, prefix="/api/v1", tags=["Natural Language Query"])

app.include_router(insider.router, prefix="/api/v1", tags=["insider"])

app.include_router(analysts.router, prefix="/api/v1", tags=["analysts"])

app.include_router(developments.router, prefix="/api/v1", tags=["Significant Developments"])

app.include_router(analytics.router)



