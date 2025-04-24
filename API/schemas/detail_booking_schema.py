from pydantic import BaseModel

class DetailBookingBase(BaseModel):
    iduser: str
    idbooking: str

class DetailBookingResponse(DetailBookingBase):
    class Config:
        from_attributes = True

class DetailBookingCreate(DetailBookingBase):
    pass