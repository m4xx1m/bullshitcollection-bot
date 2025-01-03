from enum import Enum

from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    is_moder: bool = False

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.first_name


class MediaType(Enum):
    VIDEO = "video"
    PHOTO = "photo"
    AUDIO = "audio"
    FILE = "file"
    ANIMATION = "animation"
    STICKER = "sticker"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"  # round voice message with video 


class Save(BaseModel):
    file_id: str
    caption: str
    media_type: MediaType
