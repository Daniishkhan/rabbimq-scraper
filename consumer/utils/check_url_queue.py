import pika

def check_url_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    queue_info = channel.queue_declare(queue='url_queue', durable=True, passive=True)
    message_count = queue_info.method.message_count
    
    print(f"Number of messages in url_queue: {message_count}")
    
    connection.close()

if __name__ == "__main__":
    check_url_queue()