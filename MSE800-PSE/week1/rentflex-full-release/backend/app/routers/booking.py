from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_session
from ..deps import get_current_active_user
from ..schemas.booking import BookingCreate, BookingOut
from ..services.booking_service import create_booking, get_user_bookings, cancel_booking
from ..schemas.BookingCalculate import (BookingCalculationRequest, BookingCalculationResult,)
from ..services.calculate_booking_fee import calculate_booking_fee

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# 创建预订
@router.post(
    "",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input or unavailable vehicle"},
    }
)
async def api_create_booking(
    booking_in: BookingCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
):
    booking = await create_booking(session, current_user.id, booking_in)
    return booking

# 获取当前用户的所有预订
@router.get(
    "",
    response_model=List[BookingOut],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of bookings for the user"},
    }
)
async def api_get_my_bookings(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
):
    bookings = await get_user_bookings(session, current_user.id)
    return bookings

# 取消预订
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Booking cancelled"},
        404: {"description": "Booking not found"},
        403: {"description": "Forbidden, not owner or not cancellable"},
    }
)
async def api_cancel_booking(
    id: int = Path(..., description="Booking ID"),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
):
    await cancel_booking(session, current_user.id, id)
    return None  # 204 No Content


@router.post("/calculate", response_model=BookingCalculationResult)
async def calculate_booking(
    req: BookingCalculationRequest,
    session: AsyncSession = Depends(get_session),
):
    return await calculate_booking_fee(session, req)
