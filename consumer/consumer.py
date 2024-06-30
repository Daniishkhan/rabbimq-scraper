import pika
import base64
import io
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def process_screenshot(ch, method, properties, body):
    try:
        # Convert the body to an image
        image = Image.open(io.BytesIO(body))
        
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_image = encode_image(buffered.getvalue())

        # Send to OpenAI API
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

        # Print the extracted text
        print(f"Analysis for {properties.headers['url']}:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"Error processing screenshot: {e}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='screenshot_queue')

    channel.basic_consume(queue='screenshot_queue',
                          auto_ack=True,
                          on_message_callback=process_screenshot)

    print('Waiting for screenshots. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()