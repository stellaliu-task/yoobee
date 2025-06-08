from sqlalchemy import join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status
from datetime import date, datetime

from ..schemas.BookingCalculate import BookingCalculationRequest

from ..services.calculate_booking_fee import calculate_booking_fee
from ..models import Booking, Extra, Vehicle, BookingStatus, booking_extras
from ..schemas.booking import BookingCreate, BookingOut
from sqlalchemy.orm import selectinload


async def create_booking(session: AsyncSession, user_id: int, booking_in: BookingCreate):
    # 检查车辆是否存在且可用
    vehicle = await session.get(Vehicle, booking_in.vehicle_id)
    if not vehicle or not vehicle.available_now:
        raise HTTPException(status_code=400, detail="Invalid input or unavailable vehicle")

    # 检查开始日期是否在当前日期之后
    today = date.today()
    if booking_in.start_date < today:
        raise HTTPException(status_code=400, detail="Booking start date must be today or in the future")

    # 检查时间逻辑
    if booking_in.end_date < booking_in.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    # 计算租期天数并验证是否在允许范围内
    rental_days = (booking_in.end_date - booking_in.start_date).days + 1
    if rental_days < vehicle.minimum_rent_period or rental_days > vehicle.maximum_rent_period:
        raise HTTPException(
            status_code=400, 
            detail=f"Rental period must be between {vehicle.minimum_rent_period} and {vehicle.maximum_rent_period} days"
        )

    # 检查时间冲突
    query = select(Booking).where(
        Booking.vehicle_id == booking_in.vehicle_id,
        Booking.status.in_([BookingStatus.pending, BookingStatus.approved]),
        Booking.end_date >= booking_in.start_date,
        Booking.start_date <= booking_in.end_date
    )

    result = await session.execute(query)
    conflict = result.scalars().first()
    if conflict:
        raise HTTPException(status_code=400, detail="Vehicle is already booked for the selected dates")
    
    # 1. 查 extras
    extras_objs = []
    if booking_in.extras:
        result = await session.execute(
            select(Extra).where(Extra.id.in_(booking_in.extras), Extra.active == True)
        )
        extras_objs = result.scalars().all()

    # 2. 创建
    booking = Booking(
        user_id=user_id,
        vehicle_id=booking_in.vehicle_id,
        start_date=booking_in.start_date,
        end_date=booking_in.end_date,
        status=BookingStatus.pending,
        total_fee=0  # 先占位，后面再更新
    )
    
    session.add(booking)
    await session.flush()  # 确保 booking.id 可用

    # 3. 写入多对多快照 book_extras
    for extra in extras_objs:
        await session.execute(
            booking_extras.insert().values(
                booking_id=booking.id,
                extra_id=extra.id,
                fee=extra.fee
            )
        )
    # 4. 计算 total_fee 并写入
    fee_result = await calculate_booking_fee(session, BookingCalculationRequest(
        vehicle_id=booking.vehicle_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        extras=[extra.id for extra in extras_objs]
    ))
    booking.total_fee = fee_result.total_fee
    await session.commit()
    await session.refresh(booking)

    # 组装 BookingOut，显式赋值
    return BookingOut(
        id=booking.id,
        vehicle=booking.vehicle,  # 如果 BookingOut 只要 id，可以填 vehicle_id=booking.vehicle_id
        user=booking.user,
        start_date=booking.start_date,
        end_date=booking.end_date,
        status=booking.status,
        total_fee=booking.total_fee,
        extras=fee_result.extras,           # List[BookingExtraOut]
        currency=fee_result.currency,
    )

async def get_user_bookings(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Booking)
        .options(
            selectinload(Booking.vehicle),
            selectinload(Booking.user),
            selectinload(Booking.extras)
        )
        .where(Booking.user_id == user_id))
    bookings = result.scalars().all()
    return [BookingOut.model_validate(b) for b in bookings]

async def cancel_booking(session: AsyncSession, user_id: int, booking_id: int):
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden, not owner or not cancellable")
    if booking.status not in [BookingStatus.pending, BookingStatus.approved]:
        raise HTTPException(status_code=403, detail="Booking cannot be cancelled")
    booking.status = BookingStatus.cancelled
    await session.commit()
