import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Enum
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

##############################
# BLOCK WITH DATABASE MODELS #
##############################

Base = declarative_base()


class PortalRole(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


# тип начисления з/п

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    tg_username = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(ARRAY(String), nullable=False)
    position = Column(Integer, ForeignKey("position.id"))
    point = Column(Integer, ForeignKey("point.id"))
    type_pay = Column(Integer, ForeignKey("type_pay.id"))

    visits = relationship("Visit", back_populates="user")
    position_id = relationship("Position", back_populates="users")


    @property
    def is_superadmin(self) -> bool:
        return PortalRole.ROLE_PORTAL_SUPERADMIN in self.roles

    @property
    def is_admin(self) -> bool:
        return PortalRole.ROLE_PORTAL_ADMIN in self.roles

    def enrich_admin_roles_by_admin_role(self):
        if not self.is_admin:
            return {*self.roles, PortalRole.ROLE_PORTAL_ADMIN}

    def remove_admin_privileges_from_model(self):
        if self.is_admin:
            return {role for role in self.roles if role != PortalRole.ROLE_PORTAL_ADMIN}


class TypePay(Base):
    __tablename__ = "type_pay"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)


class Position(Base):
    __tablename__ = "position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), )
    is_active = Column(Boolean(), default=True)

    category = relationship('Category', back_populates='positions')
    users = relationship('User', back_populates='position_id')


class Point(Base):
    __tablename__ = "point"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    coordinates = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    visits = relationship("Visit", back_populates="point_id")


class Visit(Base):
    __tablename__ = "visit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean(), default=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    point = Column(Integer, ForeignKey("point.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="visits")
    # на самом деле тут лучше было бы point а сверху point_id: не путаться что отношение, а что фк
    point_id = relationship("Point", back_populates="visits")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    positions = relationship('Position', back_populates='category')
