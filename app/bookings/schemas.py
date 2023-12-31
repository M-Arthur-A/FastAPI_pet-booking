from pydantic import BaseModel
from datetime import date


class SBooking(BaseModel):
    id:         int
    room_id:    int
    user_id:    int
    date_from:  date
    date_to:    date
    price:      int
    total_cost: int
    total_days: int
    image_id:   int       #(для номера)
    name:       str       #(для номера)
    description:str       #(для номера)
    services:   list[str] #(для номера)

    # class Config:              # now no need
        # from_attributes = True # old
        # orm_mode = True        # very old
