import json
import time
import pika
import threading
import os
import traceback
from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)

# Environment variables
MONGO_URI = os.getenv("MONGO_URI")  # mongodb://mongo:27017/videos
MP3_MONGO_URI = "mongodb://mongo:27017/mp3db"

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = os.getenv("QUEUE_NAME", "video")

# Globals
mongo_video_client = None
mongo_mp3_client = None
fs_videos = None
fs_mp3s = None
channel = None


def init_mongo():
    global mongo_video_client, mongo_mp3_client, fs_videos, fs_mp3s

    while True:
        try:
            # Videos DB
            mongo_video_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            mongo_video_client.admin.command("ping")
            fs_videos = gridfs.GridFS(mongo_video_client.get_default_database())

            # MP3 DB
            mongo_mp3_client = MongoClient(MP3_MONGO_URI, serverSelectionTimeoutMS=3000)
            mongo_mp3_client.admin.command("ping")
            fs_mp3s = gridfs.GridFS(mongo_mp3_client.get_default_database())

            print("MongoDB (videos + mp3db) connected")
            return
        except Exception as e:
            print("Waiting for MongoDB...", e)
            time.sleep(3)


def init_rabbitmq():
    global channel
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            print("RabbitMQ connected")
            return
        except Exception as e:
            print("Waiting for RabbitMQ...", e)
            time.sleep(3)


def background_init():
    init_mongo()
    init_rabbitmq()


threading.Thread(target=background_init, daemon=True).start()


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if err:
        return str(err), 401
    return token, 200


@server.route("/upload", methods=["POST"])
def upload():
    try:
        if fs_videos is None or channel is None:
            return "service not ready", 503

        access_data, err = validate.token(request)
        if err:
            return str(err), 401

        access_data = json.loads(access_data)

        if "file" not in request.files:
            return "no file part", 400

        file = request.files["file"]

        if file.filename == "":
            return "no selected file", 400

        err = util.upload(file, fs_videos, channel, access_data)
        if err:
            return str(err), 500

        return "upload successful", 200

    except Exception:
        traceback.print_exc()
        return "internal server error", 500


@server.route("/download", methods=["GET"])
def download():
    try:
        access_data, err = validate.token(request)
        if err:
            return err, 401

        access_data = json.loads(access_data)

        if not access_data.get("admin"):
            return "not authorized", 401

        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid is required", 400

        out = fs_mp3s.get(ObjectId(fid_string))

        return send_file(
            out,
            download_name=f"{fid_string}.mp3",
            mimetype="audio/mpeg"
        )

    except Exception as e:
        print(e)
        return "internal server error", 500


@server.route("/health", methods=["GET"])
def health():
    return "ok", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
