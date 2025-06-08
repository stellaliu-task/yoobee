from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import vehicle as vehicle_schema
from ..services import car_service
from ..database import get_session


router = APIRouter(
    tags=["Vehicles"]
)

# 用户接口 - 按租期筛选可用车辆
@router.get("/vehicles", 
            response_model=list[vehicle_schema.Vehicle],
            responses={
        400: {"description": "Bad Request", "content": {"application/json": {"example": {"detail": "Date format should be YYYY-MM-DD"}}}},
        422: {"description": "Validation Error"}
    })
async def get_vehicles(
    start: str = Query(..., description="Start date", example="2024-06-01"),
    end: str = Query(..., description="End date", example="2024-06-10"),
    session: AsyncSession = Depends(get_session)
):
    # if not start or not end:
    #     raise HTTPException(status_code=422, detail="start and end are required")

    # 日期格式判断
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format should be YYYY-MM-DD")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    return await car_service.get_available_vehicles(session, start_date, end_date)

# 用户接口 - 获取车辆详情
@router.get("/vehicles/{id}", response_model=vehicle_schema.Vehicle)
async def get_vehicle_detail(id: int, session: AsyncSession = Depends(get_session)):
    vehicle = await car_service.get_vehicle_by_id(session, id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

