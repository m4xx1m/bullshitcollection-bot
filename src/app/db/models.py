from sqlalchemy import BigInteger, Enum, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from . import dto


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    is_moder: Mapped[bool] = mapped_column(insert_default=False)
    
    @classmethod
    def from_dto(cls, v: dto.User):
        return cls(
            user_id=v.user_id,
            first_name=v.first_name,
            last_name=v.last_name,
            username=v.username,
            is_moder=v.is_moder,
        )

    def to_dto(self) -> dto.User:
        return dto.User(
            user_id=self.user_id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            is_moder=self.is_moder,
        )
        

class Save(Base):
    __tablename__ = "saves"
    __table_args__ = (
        UniqueConstraint("id", "file_id"),
    )

        
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(unique=True)
    caption: Mapped[str]
    media_type = mapped_column(Enum(dto.MediaType, name="media_type"))
    
    @classmethod
    def from_dto(cls, v: dto.Save):
        return cls(
            file_id=v.file_id,
            caption=v.caption,
            media_type=v.media_type,
        )

    def to_dto(self) -> dto.Save:
        return dto.Save(
            file_id=self.file_id,
            caption=self.caption,
            media_type=self.media_type,
        )
