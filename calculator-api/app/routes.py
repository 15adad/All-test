from fastapi import APIRouter, HTTPException
from app.models import CalculationRequest, CalculationResponse
from app.calculator import calculate

router = APIRouter(prefix="/api", tags=["计算器"])

@router.post("/calculate", response_model=CalculationResponse)
async def calc(request: CalculationRequest):
    """
    执行四则运算
    """
    try:
        result, message = calculate(request.a, request.b, request.operation)
        return CalculationResponse(
            a=request.a,
            b=request.b,
            operation=request.operation,
            result=result,
            message=message
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="除数不能为 0")

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "计算器服务运行正常"}

@router.get("/")
async def root():
    return {
        "message": "欢迎使用计算器 API",
        "docs": "/docs",
        "redoc": "/redoc"
    }