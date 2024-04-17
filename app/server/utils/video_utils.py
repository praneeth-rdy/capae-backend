import cv2
import ffmpeg

import time
import os
from bson import ObjectId

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


def detect_video(input_file, output_file, model=model, fps=30, score_filter=0.6):
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

    temp_file = 'temp.mp4'
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
    out = cv2.VideoWriter(temp_file, cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

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
    ffmpeg.input(temp_file).output(output_file).run()
    os.remove(temp_file)


async def detect_video_and_set_db(entry_id):
    input_file = os.path.join('app/', MEDIA_PATH, entry_id, INPUT_FILE_PATH)
    output_file = os.path.join('app/', MEDIA_PATH, entry_id, OUTPUT_FILE_PATH)
    update_data = None
    try:
        start_time = time.time()
        detect_video(input_file=input_file, output_file=output_file)
        duration = get_formatted_time(time.time() - start_time)
        update_data = UpdateOutputVideoSuccess(runtime=duration)
    except:
        update_data = UpdateOutputVideoError()
    updated_entry = await parsed_video_collection.find_one_and_update({'_id': ObjectId(entry_id)}, {'$set': update_data.dict()})
    return updated_entry
