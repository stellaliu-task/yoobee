from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class BookingCalculationRequest(BaseModel):
    vehicle_id: int
    start_date: date
    end_date: date
    extras: Optional[List[int]] = []  # 传 extra 的 id 列表


class CalculationAdditionalCharge(BaseModel):
    name: str
    fee: float

class BookingExtraOut(BaseModel):
    id: int
    name: str
    fee: float
    currency: Optional[str] = "NZD"
    class Config:
        from_attributes = True


class BookingCalculationResult(BaseModel):
    vehicle_id: int
    start_date: str
    end_date: str
    days: int
    base_fee: float                # 基础租金（如车辆单价 * 天数）
    extras: List[BookingExtraOut]
    discount: float = 0.0
    additional_charges: Optional[List[CalculationAdditionalCharge]] = []
    total_fee: float
    currency: str = "NZD"

    class Config:
        from_attributes = True
