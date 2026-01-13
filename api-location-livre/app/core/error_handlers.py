from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BusinessError, NotFoundError, ValidationRuleError

def install_error_handlers(app: FastAPI):
    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        status = 422 if isinstance(exc, ValidationRuleError) else 404 if isinstance(exc, NotFoundError) else 400
        return JSONResponse(status_code=status, content={"error": exc.code, "detail": exc.message})
