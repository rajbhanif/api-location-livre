from fastapi import FastAPI

from app.db.session import Base, engine
from app.core.error_handlers import install_error_handlers

from app.routers.catalogue import router as catalogue_router
from app.routers.livres import router as livres_router
from app.routers.prets import router as prets_router
from app.routers.reservations import router as reservations_router
from app.routers.notifications import router as notifications_router
from app.routers.audit import router as audit_router
from app.routers.amendes import router as amendes_router
from app.routers.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="API Location Livre")

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)

        install_error_handlers(app)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(catalogue_router, prefix="/api/v1")
    app.include_router(livres_router, prefix="/api/v1")
    app.include_router(prets_router, prefix="/api/v1")
    app.include_router(reservations_router, prefix="/api/v1")
    app.include_router(notifications_router, prefix="/api/v1")
    app.include_router(amendes_router, prefix="/api/v1")
    app.include_router(audit_router, prefix="/api/v1")

    return app


app = create_app()
