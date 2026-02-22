import pika
import sys
import os
import time
import json
from send import email


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
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    mp3_queue = os.getenv("MP3_QUEUE")  # MUST match converter queue name

    if not mp3_queue:
        print("❌ MP3_QUEUE not set")
        sys.exit(1)

    connection = wait_for_rabbitmq(rabbit_host)
    channel = connection.channel()

    # Make queue durable
    channel.queue_declare(queue=mp3_queue, durable=True)

    # Process one message at a time (important)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        print("📩 Received message from MP3 queue")

        try:
            # RabbitMQ sends bytes → decode → parse JSON
            message = json.loads(body.decode())

            err = email.notification(message)

            if err:
                print("❌ Email failed, requeueing:", err)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                print("✅ Email sent successfully")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print("❌ Processing crashed:", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=mp3_queue, on_message_callback=callback)

    print("📨 Notification service waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
