from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/")
def root():
    return {
        "message": "Welcome to AI Chat Backend"
    }


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Chat Backend is runing"
    }