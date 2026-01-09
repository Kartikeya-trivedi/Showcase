from fastapi import APIRouter
from app.api.v1 import resume, portfolio, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume Processing"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio Management"])
