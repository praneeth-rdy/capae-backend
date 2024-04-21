import cv2

# import ffmpeg

import time
import os
from bson import ObjectId

import asyncio
from concurrent.futures import ThreadPoolExecutor

from torchvision import transforms
from detecto import core
from tqdm import tqdm
from detecto.utils import normalize_transform

from app.server.static.constants import MEDIA_PATH, INPUT_FILE_PATH, OUTPUT_FILE_PATH
from app.server.models.parsed_video import UpdateOutputVideoSuccess, UpdateOutputVideoError
from app.server.config.databases import db
from app.server.utils.date_utils import get_formatted_time

parsed_video_collection = db.get_collection('parsed_videos')

model = core.Model.load('app/data/Train.pth', ['1', '2', '3', '4', '5'])


def detect_video(input_file, output_file, temp_file, model=model, fps=30, score_filter=0.6):
    """Takes in a video and produces an output video with object detection
    run on it (i.e. displays boxes around detected objects in real-time).
    Output videos should have the .avi file extension. Note: some apps,
    such as macOS's QuickTime Player, have difficulty viewing these
    output videos. It's recommended that you download and use
    `VLC <https://www.videolan.org/vlc/index.html>`_ if this occurs.


    :param model: The trained model with which to run object detection.
    :type model: detecto.core.Model
    :param input_file: The path to the input video.
    :type input_file: str
    :param output_file: The name of the output file. Should have a .avi
        file extension.
    :type output_file: str
    :param fps: (Optional) Frames per second of the output video.
        Defaults to 30.
    :type fps: int
    :param score_filter: (Optional) Minimum score required to show a
        prediction. Defaults to 0.6.
    :type score_filter: float

    **Example**::

        >>> from detecto.core import Model
        >>> from detecto.visualize import detect_video

        >>> model = Model.load('model_weights.pth', ['tick', 'gate'])
        >>> detect_video(model, 'input_vid.mp4', 'output_vid.avi', score_filter=0.7)
    """

    # Read in the video
    video = cv2.VideoCapture(input_file)

    # Video frame dimensions
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Scale down frames when passing into model for faster speeds
    scaled_size = 800
    scale_down_factor = min(frame_height, frame_width) / scaled_size

    # The VideoWriter with which we'll write our video with the boxes and labels
    # Parameters: filename, fourcc, fps, frame_size
    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

    # Transform to apply on individual frames of the video
    transform_frame = transforms.Compose([transforms.ToPILImage(), transforms.Resize(scaled_size), transforms.ToTensor(), normalize_transform()])  # TODO Issue #16

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create a tqdm progress bar with the total number of frames
    pbar = tqdm(total=total_frames, desc='Processing Frames')

    # tracker = cv2.Tracker_create(args["tracker"].upper())

    # Loop through every frame of the video
    while True:
        # start_time = time.time()
        ret, frame = video.read()
        # Stop the loop when we're done with the video
        if not ret:
            break

        # The transformed frame is what we'll feed into our model
        # transformed_frame = transform_frame(frame)
        transformed_frame = frame  # TODO: Issue #16
        predictions = model.predict(transformed_frame)

        # Add the top prediction of each class to the frame
        for label, box, score in zip(*predictions):
            if score < score_filter:
                continue

            # Since the predictions are for scaled down frames,
            # we need to increase the box dimensions
            # box *= scale_down_factor  # TODO Issue #16

            # Create the box around each object detected
            # Parameters: frame, (start_x, start_y), (end_x, end_y), (r, g, b), thickness
            xmin, ymin, xmax, ymax = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # Green rectangle

            cv2.putText(frame, f'{label}: {round(score.item(), 2)}', (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        # Write this frame to our video file
        out.write(frame)
        pbar.update(1)
        # print(f'\nThis much time for a frame: {time.time() - start_time}\n')

        # If the 'q' key is pressed, break from the loop
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # When finished, release the video capture and writer objects
    video.release()
    out.release()

    # Close all the frames
    cv2.destroyAllWindows()
    # ffmpeg.input(temp_file).output(output_file).run()
    # os.remove(temp_file)


def detect_with_tracker(input_file, output_file, temp_file, model=model, fps=30, score_filter=0.6):
    # Read in the video
    video = cv2.VideoCapture(input_file)

    # Video frame dimensions
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Scale down frames when passing into model for faster speeds
    scaled_size = 800
    scale_down_factor = min(frame_height, frame_width) / scaled_size

    # The VideoWriter with which we'll write our video with the boxes and labels
    # Parameters: filename, fourcc, fps, frame_size
    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

    # Transform to apply on individual frames of the video
    transform_frame = transforms.Compose([transforms.ToPILImage(), transforms.Resize(scaled_size), transforms.ToTensor(), normalize_transform()])  # TODO Issue #16

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create a tqdm progress bar with the total number of frames
    pbar = tqdm(total=total_frames, desc='Processing Frames')

    # Initialize trackers list
    trackers = []
    num_objects = -1
    max_cnt = 0
    COUNT_UNTIL = 3
    cur_cnt = 0

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Run object detection until 5 objects are detected
        if num_objects == -1:
            # print("Counting Objects")
            transformed_frame = frame  # TODO: Apply transformation
            predictions = model.predict(transformed_frame)
            cnt = 0

            # Initialize trackers for up to 5 detected objects
            for label, box, score in zip(*predictions):
                if score < score_filter:
                    continue
                bbox = (int(box[0]), int(box[1]), int(box[2] - box[0]), int(box[3] - box[1]))

                ## draw rectangle
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f'{label}: {round(score.item(), 2)}', (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                cnt += 1

            max_cnt = max(max_cnt, cnt)
            cur_cnt += 1

            if cur_cnt >= COUNT_UNTIL:
                #   print("Objects Found: ",max_cnt)
                num_objects = max_cnt
                cur_cnt = 0
                max_cnt = 0
        elif len(trackers) < num_objects:
            trackers = []

            transformed_frame = frame  # TODO: Apply transformation
            predictions = model.predict(transformed_frame)

            # Initialize trackers for up to 5 detected objects
            for label, box, score in zip(*predictions):
                if score < score_filter:
                    continue
                bbox = (int(box[0]), int(box[1]), int(box[2] - box[0]), int(box[3] - box[1]))

                ## draw rectangle
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f'{label}: {round(score.item(), 2)}', (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                ## create tracker for this object
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, bbox)
                trackers.append([tracker, label, score.item()])
                if len(trackers) == num_objects:
                    break
            # print("Objects Detected: ",len(trackers))
        else:
            # Update existing trackers
            flag = 1
            for tracker, label, score in trackers:
                ret, bbox = tracker.update(frame)
                if not ret:
                    # If tracker fails, reset all trackers and break
                    flag = 0
                else:
                    # Tracking successful, draw bounding box
                    xmin, ymin, w, h = (int(coord) for coord in bbox)
                    cv2.rectangle(frame, (xmin, ymin), (xmin + w, ymin + h), (0, 255, 0), 2)
                    cv2.putText(frame, f'{label}: {round(score, 2)}', (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

            if flag == 0:
                #   print("Tracking failed")
                trackers = []
                num_objects = -1
                cur_cnt = 0
                max_cnt = 0

        # Write frame to video
        out.write(frame)
        pbar.update(1)

        # Exit loop if 'q' key is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Release resources
    video.release()
    out.release()
    cv2.destroyAllWindows()
    # ffmpeg.input(temp_file).output(output_file).run()
    # os.remove(temp_file)


async def detect_video_and_set_db(entry_id):
    input_file = os.path.join('app/', MEDIA_PATH, entry_id, INPUT_FILE_PATH)
    output_file = os.path.join('app/', MEDIA_PATH, entry_id, OUTPUT_FILE_PATH)
    temp_file = os.path.join('app/', MEDIA_PATH, entry_id, 'temp.mp4')
    update_data = None
    try:
        start_time = time.time()
        with ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(executor, detect_with_tracker, input_file, output_file, temp_file)
        # await detect_video(input_file=input_file, output_file=output_file)
        duration = get_formatted_time(time.time() - start_time)
        update_data = UpdateOutputVideoSuccess(runtime=duration)
    except Exception as e:
        print(e)
        update_data = UpdateOutputVideoError()
    updated_entry = await parsed_video_collection.find_one_and_update({'_id': ObjectId(entry_id)}, {'$set': update_data.dict()})
    return updated_entry
