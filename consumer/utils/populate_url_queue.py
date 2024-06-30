import pika
import json

def populate_url_queue(urls):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.queue_declare(queue='url_queue', durable=True)
    
    for url in urls:
        channel.basic_publish(
            exchange='',
            routing_key='url_queue',
            body=json.dumps({'url': url}),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
    
    print(f"Added {len(urls)} URLs to the queue")
    connection.close()

# Example usage
urls = [
    "https://www.ai-synapse.com",
    "https://google.com",
    "https://moneypex.com",
    "https://stackoverflow.com",
    "https://www.linkedin.com",
    "https://www.dawn.com",
    "https://www.nytimes.com",
]

populate_url_queue(urls)