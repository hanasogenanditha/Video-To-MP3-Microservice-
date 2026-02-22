import pika
import sys
import os
import time
from pymongo import MongoClient
import gridfs
from convert import to_mp3


def wait_for_mongo(uri):
    while True:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            print("✅ Connected to MongoDB")
            return client
        except Exception as e:
            print("⏳ Waiting for MongoDB...", e)
            time.sleep(3)


def wait_for_rabbitmq(host):
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host)
            )
            print("✅ Connected to RabbitMQ")
            return connection
        except Exception as e:
            print("⏳ Waiting for RabbitMQ...", e)
            time.sleep(3)


def main():
    mongo_uri = os.getenv("MONGO_URI")  # should be mongodb://mongo:27017
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    video_queue = os.getenv("VIDEO_QUEUE")

    if not mongo_uri:
        print("❌ MONGO_URI not set")
        sys.exit(1)

    if not video_queue:
        print("❌ VIDEO_QUEUE not set")
        sys.exit(1)

    # Mongo connection
    client = wait_for_mongo(mongo_uri)

    # 🔥 TWO DATABASES (correct wiring)
    db_videos = client["videos"]   # where gateway stored uploaded videos
    db_mp3s = client["mp3db"]      # where we store converted mp3s

    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # RabbitMQ connection
    connection = wait_for_rabbitmq(rabbit_host)
    channel = connection.channel()

    # Ensure queue exists
    channel.queue_declare(queue=video_queue, durable=True)

    def callback(ch, method, properties, body):
        print("📩 Received message")

        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)

        if err:
            print("❌ Processing failed, requeueing")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            print("✅ Processing done")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=video_queue, on_message_callback=callback)

    print("🎧 notification waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
