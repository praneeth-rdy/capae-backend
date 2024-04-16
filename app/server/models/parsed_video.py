from pydantic import BaseModel

from app.server.static.enums import Status


class ParsedVideo(BaseModel):
    """
    Container for a single record of parsed-video
    """

    status: Status = Status.IN_PROCESS  # in-process, done, error


class UpdateOutputVideoSuccess(BaseModel):
    """
    Model to update the output of the parsed-video
    """

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
