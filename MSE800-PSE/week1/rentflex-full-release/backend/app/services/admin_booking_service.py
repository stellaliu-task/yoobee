from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Booking, BookingStatus
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

async def get_all_bookings(session: AsyncSession, status: str = None):
    stmt = select(Booking).options(
        selectinload(Booking.vehicle),
        selectinload(Booking.user),
        selectinload(Booking.extras)
    )
    if status:
        # 校验 status 合法性
        try:
            status_enum = BookingStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status value")
        stmt = stmt.where(Booking.status == status_enum)
    result = await session.execute(stmt)
    return result.scalars().all()

async def approve_booking(session: AsyncSession, booking_id: int):
    result = await session.execute(
        select(Booking)
        .options(selectinload(Booking.vehicle), selectinload(Booking.user))
        .where(Booking.id == booking_id)
    )
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is not pending")
    booking.status = BookingStatus.approved
    await session.commit()
    await session.refresh(booking)
    return booking

async def reject_booking(session: AsyncSession, booking_id: int):
    result = await session.execute(
        select(Booking)
        .options(selectinload(Booking.vehicle), selectinload(Booking.user))
        .where(Booking.id == booking_id)
    )
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is not pending")
    booking.status = BookingStatus.rejected
    await session.commit()
    await session.refresh(booking)
    return booking
