from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import Base, engine
from app.routers import auth, products, suppliers, purchase_orders, etl
from app.scheduler.reorder_job import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)  # Create tables if not exist
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="InventoryIQ",
    description=(
        "## Automated Inventory & Supplier Management System\n\n"
        "A production-grade backend for managing products, suppliers, and purchase orders.\n\n"
        "### Features\n"
        "- JWT Authentication (Admin / Viewer roles)\n"
        "- Full CRUD for Products, Suppliers, Purchase Orders\n"
        "- Automated reorder alerts via APScheduler\n"
        "- CSV ETL pipeline with Pandas\n"
        "- S3 integration for file storage\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(purchase_orders.router)
app.include_router(etl.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "InventoryIQ", "version": "1.0.0"}
