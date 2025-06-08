from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from ..database import get_session
from ..services.admin_booking_service import (
    get_all_bookings,
    approve_booking,
    reject_booking,
)
from ..schemas.booking import BookingOut
from ..deps import get_admin_user

router = APIRouter(
    prefix="/admin/bookings",
    tags=["AdminBookings"],
    dependencies=[Depends(get_admin_user)]  # 全部接口都需要 admin
)

@router.get("", response_model=List[BookingOut])
async def admin_get_bookings(
    status: Optional[str] = Query(None, description="pending/approved/rejected/cancelled"),
    session: AsyncSession = Depends(get_session)
):
    bookings = await get_all_bookings(session, status)
    return bookings

@router.post("/{id}/approve", response_model=BookingOut)
async def admin_approve_booking(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    booking = await approve_booking(session, id)
    return booking

@router.post("/{id}/reject", response_model=BookingOut)
async def admin_reject_booking(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    booking = await reject_booking(session, id)
    return booking
