import pika
import base64
import io
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json
import logging
import atexit

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database connection
try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432")
    )
    logging.info("Successfully connected to the database")
except Exception as e:
    logging.error(f"Error connecting to the database: {e}")
    raise

def close_db_connection():
    if conn and not conn.closed:
        conn.close()
        logging.info("Database connection closed")

atexit.register(close_db_connection)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def store_result(url, analysis):
    logging.info(f"Attempting to store result for {url}")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO website_analyses (url, analysis) VALUES (%s, %s)",
                (url, Json(analysis))
            )
        conn.commit()
        logging.info(f"Analysis for {url} successfully stored in database")
    except Exception as e:
        logging.error(f"Error storing result for {url}: {e}")
        conn.rollback()

def process_screenshot(ch, method, properties, body):
    url = properties.headers.get('url', 'Unknown URL')
    logging.info(f"Processing screenshot for {url}")
    try:
        image = Image.open(io.BytesIO(body))
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_image = encode_image(buffered.getvalue())

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction specialist. Please extract the text from the image and return it in a structured format."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
        )
        
        analysis = response.choices[0].message.content
        logging.info(f"Analysis received for {url}")
        
        store_result(url, analysis)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info(f"Processing completed for {url}")

    except Exception as e:
        logging.error(f"Error processing screenshot for {url}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='screenshot_queue', durable=False)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='screenshot_queue', on_message_callback=process_screenshot)

        logging.info('Waiting for screenshots. To exit press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == '__main__':
    main()