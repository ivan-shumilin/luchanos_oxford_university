import re
import uuid
from typing import Optional
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator


#########################
# BLOCK WITH API MODELS #
#########################

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")
PHONE_MATCH_PATTERN = re.compile(r"[0-9]{10}$")


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    patronymic: str
    tg_username: str
    email: EmailStr
    phone: str
    is_active: bool
    position: int
    point: int
    type_pay: int


class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    tg_username: str
    email: EmailStr
    phone: str
    password: str
    position: int
    point: int
    type_pay: int

    @validator("name")
    def validate_name(cls, value):
        if value == "":
            raise HTTPException(
                status_code=422, detail={"name": "Укажите имя"}
            )
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail={"name": "Имя должно состоять из букв"}
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if value == "":
            raise HTTPException(
                status_code=422, detail={"surname": "Укажите фамилию"}
            )
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail={"surname": "Фамилия должна состоять из букв"}
            )
        return value

    # @validator("patronymic")
    # def validate_patronymic(cls, value):
    #     if not LETTER_MATCH_PATTERN.match(value) and value is not None:
    #         raise HTTPException(
    #             status_code=422, detail="Surname should contains only letters"
    #         )
    #     return value
    #
    # @validator("phone")
    # def validate_phone(cls, value):
    #     if not PHONE_MATCH_PATTERN.match(value):
    #         raise HTTPException(
    #             status_code=422, detail="The number must consist of ten digits"
    #         )
    #     return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: uuid.UUID


class ShowPosition(TunedModel):
    id: int
    name: str
    is_active: bool


class PositionCreate(BaseModel):
    name: str


class PointCreate(BaseModel):
    name: str
    address: str
    coordinates: str


class ShowPoint(TunedModel):
    id: int
    name: str
    address: str
    coordinates: str
    is_active: bool



class TypePayCreate(TunedModel):
    name: str


class TypePayShow(TunedModel):
    id: int
    name: str
    is_active: bool


class VisitCreate(TunedModel):
    user_id: uuid.UUID
    point: int


class VisitShow(TunedModel):
    id: int
    user_id: uuid.UUID
    point: int
    created_at: datetime
    is_active: bool

