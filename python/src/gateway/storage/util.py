import json
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = os.getenv("QUEUE_NAME", "video")

def upload(f, fs, channel_unused, access):
    try:
        fid = fs.put(
            f.stream,
            filename=f.filename,
            content_type=f.content_type
        )
        print("Stored file in Mongo with id:", fid)
    except Exception as e:
        print("Mongo store failed:", e)
        return "file storage failed"

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        # 🔥 CREATE NEW CONNECTION PER REQUEST
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

        connection.close()
        print("Message sent to queue")

    except Exception as e:
        print("Rabbit publish failed:", e)
        fs.delete(fid)
        return "queue publish failed"

    return None
