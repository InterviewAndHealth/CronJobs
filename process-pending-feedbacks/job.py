import json
import os

import pika
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

# Postgres
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("INTERVIEW_SERVICE_DB")

# RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")
SCHEDULER_QUEUE = os.getenv("SCHEDULER_QUEUE")
CONVERSATION_QUEUE = os.getenv("CONVERSATION_QUEUE")

# Feedback delay
FEEDBACK_DELAY = os.getenv("FEEDBACK_DELAY")

required_env_vars = [
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USERNAME,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    EXCHANGE_NAME,
    SCHEDULER_QUEUE,
    CONVERSATION_QUEUE,
    FEEDBACK_DELAY,
]

if not all(required_env_vars):
    raise ValueError("Environment variables not set")

FEEDBACK_DELAY = int(FEEDBACK_DELAY)


def get_pending_feedbacks(cursor):
    query = "SELECT interviewid, feedback_status FROM interviews WHERE feedback_status = 'pending';"
    cursor.execute(query)
    results = cursor.fetchall()
    print(f"Pending feedbacks: {[result[0] for result in results]}")
    return results


def schedule_feedback(channel, interview_id, seconds):
    event = {
        "type": "SCHEDULE_EVENT",
        "data": {
            "id": f"feedback_{interview_id}",
            "seconds": seconds,
            "service": CONVERSATION_QUEUE,
            "type": "GENERATE_REPORT",
            "data": {"interview_id": interview_id},
        },
    }
    channel.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=SCHEDULER_QUEUE, body=json.dumps(event)
    )
    print(f"Scheduled feedback for interview {interview_id} in {seconds} seconds.")


def schedule_feedbacks(channel, pending_feedbacks):
    for index, (interview_id, _) in enumerate(pending_feedbacks):
        schedule_feedback(channel, interview_id, index * FEEDBACK_DELAY * 60 + 1)


if __name__ == "__main__":
    # Create a connection to Postgres
    postgres_connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
    )
    cursor = postgres_connection.cursor()

    # Create a connection to RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
    )
    rabbitmq_connection = pika.BlockingConnection(parameters)
    channel = rabbitmq_connection.channel()

    # Process pending feedbacks
    pending_feedbacks = get_pending_feedbacks(cursor)
    schedule_feedbacks(channel, pending_feedbacks)

    # Close the connections
    cursor.close()
    postgres_connection.close()
    rabbitmq_connection.close()
