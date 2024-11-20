import json
import os
from datetime import datetime

import pika
from dotenv import load_dotenv

load_dotenv(override=True)

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")
QUEUES = os.getenv("QUEUES")
NO_OF_EVENTS = os.getenv("NO_OF_EVENTS")

if not RABBITMQ_URL or not EXCHANGE_NAME or not QUEUES or not NO_OF_EVENTS:
    raise ValueError("Environment variables not set")

QUEUES = QUEUES.split(",")
NO_OF_EVENTS = int(NO_OF_EVENTS)


def publish_fake_event(channel):
    event = {"type": "keepalive", "data": {"timestamp": datetime.now().isoformat()}}
    fake_event = json.dumps(event)

    for queue in QUEUES * NO_OF_EVENTS:
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=queue,
            body=fake_event,
        )
        print(f"Published keepalive event to {queue}")


if __name__ == "__main__":
    # Create a connection and a channel
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Publish fake events
    publish_fake_event(channel)

    # Close the connection
    connection.close()
