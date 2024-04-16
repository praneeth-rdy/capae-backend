import os
import shutil

from fastapi import Request, UploadFile

from app.server.utils.video_utils import detect_video_and_set_db
from app.server.static.constants import MEDIA_PATH, INPUT_FILE_PATH
from app.server.config.databases import db
from app.server.models.parsed_video import ParsedVideo

parsed_video_collection = db.get_collection('parsed_videos')


async def temporary(name: str, request: Request):
    """
    Temporary router that works as a template to services

    Args:
        name: Any random string
    Returns:
        - Required JSON Data
    """
    print('Inside the service', name)
    return {}


async def process_video(video_file: UploadFile, request: Request):
    # create the mongodb entry
    new_video = ParsedVideo()
    created_entry = await parsed_video_collection.insert_one(new_video.dict())
    created_id = str(created_entry.inserted_id)
    new_folder_path = os.path.join('app/', MEDIA_PATH, created_id)

    os.makedirs(new_folder_path, exist_ok=True)
    new_video_path = os.path.join(new_folder_path, INPUT_FILE_PATH)

    # save the input video in the folder with uuid
    with open(new_video_path, 'wb') as buffer:
        shutil.copyfileobj(video_file.file, buffer)

    await detect_video_and_set_db(created_id)

    return {'filename': video_file.filename}


async def get_parsed_videos(request: Request):
    """
    Fetches and returns all the parsed videos saved in the db

    Args: None
    Returns:
        - Required JSON Data
    """
    documents = await parsed_video_collection.find({}).to_list(length=None)
    for doc in documents:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
    return documents


# async def update_target_info(entry_id: str, data: UpdateParsedResumeActualInfo, request: Request):
#     """
#     Asynchronously updates the target info of the parsed resume with parsed_id

#     Args:
#         parsed_id: The id of the document that needs to be updated
#         data: Object with the required target_info
#         request: A request object that has all the relevant data
#     Returns:
#         - JSON Data with all the relevant parsed-resume details
#     """
#     updated_entry = await parsed_resumes_collection.find_one_and_update({'_id': ObjectId(entry_id)}, {'$set': data.dict()})

#     if updated_entry:
#         return data.dict()

#     raise HTTPException(status_code=404, detail='Entry with the given id not found')
