from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator
from typing import Any

class VehicleBase(BaseModel):
    make: str
    model: str
    year: int
    mileage: int
    available_now: bool
    minimum_rent_period: int
    maximum_rent_period: int
    seats: int
    price_per_day: float
    image_url: str 


    # 年份合理范围
    @field_validator("year")
    @classmethod
    def valid_year(cls, v: int) -> int:
        year_now = datetime.now().year
        if v < 1980 or v > year_now + 1:
            raise ValueError("year value is not in range")
        return v

    # 里程必须非负
    @field_validator("mileage")
    @classmethod
    def valid_mileage(cls, v: int) -> int:
        if v < 0:
            raise ValueError("mileage value is not in range")
        return v

    # 座位数正整数
    @field_validator("seats")
    @classmethod
    def valid_seats(cls, v: int) -> int:
        if v <= 0 or v > 8:
            raise ValueError("seats value is not in range")
        return v


    # 价格正数
    @field_validator("price_per_day")
    @classmethod
    def valid_price(cls, v: float) -> float:
        if v <= 0 or v > 10000:
            raise ValueError("price value is not in range")
        return v

    # 图片URL简单校验
    @field_validator("image_url")
    @classmethod
    def valid_url(cls, v: str) -> str:
        if not v.startswith("http"):
            raise ValueError("Invalid image_url")
        return v
    
    # 租期范围合理
    @field_validator("minimum_rent_period", "maximum_rent_period")
    @classmethod
    def valid_period(cls, v: int, info: Any) -> int:
        if v <= 0 or v > 365:
            raise ValueError("rental period must be 1~365")
        return v

    # 租期逻辑校验：最大天数 >= 最小天数
    @field_validator("maximum_rent_period")
    @classmethod
    def valid_min_max(cls, v: int, info: Any) -> int:
        # info.data 取到同一 Model 的所有字段
        min_period = info.data.get("minimum_rent_period")
        if min_period is not None and v < min_period:
            raise ValueError("maximum_rent_period must be >= minimum_rent_period")
        return v

class VehicleCreate(VehicleBase):
     # 必填字符串字段不能为空
    @model_validator(mode="before")
    @classmethod
    def all_fields_required(cls, values: dict) -> dict:
        for k, v in values.items():
            if v is None or (isinstance(v, str) and not v.strip()):
                raise ValueError(f"{k} Field required")
        return values

class VehicleUpdate(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    mileage: int | None = None
    available_now: bool | None = None
    minimum_rent_period: int | None = None
    maximum_rent_period: int | None = None
    seats: int | None = None
    price_per_day: float | None = None
    image_url: str | None = None


class Vehicle(VehicleBase):
    id: int
    
    class Config:
        from_attributes = True
