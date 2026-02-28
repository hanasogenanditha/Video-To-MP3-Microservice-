import pika
import json
import tempfile
import os
from bson.objectid import ObjectId
from moviepy.editor import VideoFileClip


def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_video_path = temp_video.name

    try:
        # Download video from GridFS
        grid_out = fs_videos.get(ObjectId(message["video_fid"]))
        temp_video.write(grid_out.read())
        temp_video.close()

        print("Video downloaded, starting audio extraction")

        # Extract audio
        video = VideoFileClip(temp_video_path)
        audio = video.audio

        temp_mp3_path = temp_video_path.replace(".mp4", ".mp3")

        audio.write_audiofile(
            temp_mp3_path,
            codec="mp3",
            logger=None  # prevents hanging progress bar
        )

        video.close()
        audio.close()

        print("🎵 Audio extracted")

        # Save MP3 to GridFS
        with open(temp_mp3_path, "rb") as f:
            mp3_fid = fs_mp3s.put(f.read(), filename="audio.mp3")

        # Cleanup temp files
        os.remove(temp_video_path)
        os.remove(temp_mp3_path)

        message["mp3_fid"] = str(mp3_fid)

        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

        print("MP3 message sent to queue")
        return None

    except Exception as e:
        print("MP3 conversion failed:", e)
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        return "conversion failed"
