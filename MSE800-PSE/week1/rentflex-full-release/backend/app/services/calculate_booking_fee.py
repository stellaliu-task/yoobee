from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from typing import List
from ..models import Vehicle, Extra
from ..schemas.BookingCalculate import (BookingCalculationRequest, BookingCalculationResult,BookingExtraOut,)

async def calculate_booking_fee(
    session: AsyncSession,
    req: BookingCalculationRequest
) -> BookingCalculationResult:
    # 1. 查询车辆
    vehicle = await session.get(Vehicle, req.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # 2. 计算租赁天数
    days = (req.end_date - req.start_date).days + 1
    if days <= 0:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    # 3. 计算基础费用
    base_fee = days * vehicle.price_per_day

    # 4. 处理 extras
    extras_result: List[BookingExtraOut] = []
    total_extras_fee = 0.0
    if req.extras:
        result = await session.execute(
            select(Extra).where(
                Extra.id.in_(req.extras),
                Extra.active == True
            )
        )
        extras = result.scalars().all()
        for extra in extras:
            # 只要 extra 存在并启用，就加进去
            extras_result.append(BookingExtraOut(
                id=extra.id,
                name=extra.name,
                fee=extra.fee,
                currency="NZD"
            ))
            total_extras_fee += extra.fee

    # 5. 不考虑优惠和附加费
    discount = 0.0
    additional_charges = []

    # 6. 汇总总价
    total_fee = base_fee + total_extras_fee

    return BookingCalculationResult(
        vehicle_id=vehicle.id,
        start_date=str(req.start_date),
        end_date=str(req.end_date),
        days=days,
        base_fee=base_fee,
        extras=extras_result,
        discount=discount,
        additional_charges=additional_charges,
        total_fee=total_fee,
        currency="NZD"
    )
