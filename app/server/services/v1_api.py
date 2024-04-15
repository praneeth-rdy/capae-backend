# from bson import ObjectId

from fastapi import Request, UploadFile


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


async def process_video(file: UploadFile, request: Request):
    return {'filename': file.filename}


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
