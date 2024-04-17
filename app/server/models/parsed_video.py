from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.server.static.enums import Status


class ParsedVideo(BaseModel):
    """
    Container for a single record of parsed-video
    """

    name: str
    status: Status = Status.IN_PROCESS  # in-process, done, error
    runtime: Optional[str] = None
    createdAt: datetime


class UpdateOutputVideoSuccess(BaseModel):
    """
    Model to update the output of the parsed-video
    """

    runtime: str
    status: Status = Status.DONE


class UpdateOutputVideoError(BaseModel):
    """
    Model to update the error status
    """

    status: Status = Status.ERROR


class ParsedVideoCollection(BaseModel):
    """
    Model to list all the parsed-videos
    """

    parsed_videos: list[ParsedVideo]
