from typing import Any

from fastapi import APIRouter, Request, UploadFile

from app.server.services import v1_api

# Create the router
v1_api_router = APIRouter()


@v1_api_router.get('/temporary', summary='A temporary route to test the backend')
async def temporary(name: str, request: Request) -> dict[str, Any]:
    res_data = await v1_api.temporary(name, request)
    return {'status': 'SUCCESS', 'data': res_data}


@v1_api_router.post('/upload_file', summary='Saves and processes the video file')
async def process_video_route(video_file: UploadFile, request: Request) -> dict[str, Any]:
    res_data = await v1_api.process_video(video_file, request)
    return {'status': 'SUCCESS', 'data': res_data}


@v1_api_router.get('/parsed-videos', summary='Returns all the parsed videos saved in the database')
async def get_parsed_videos_route(request: Request) -> dict[str, Any]:
    res_data = await v1_api.get_parsed_videos(request)
    return {'status': 'SUCCESS', 'data': res_data}
