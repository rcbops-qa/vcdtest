import pika

connection = pike.BlockingConnection(pika.ConnectionParameters('host'))
channel = connection.channel()
channel.queue_declare(queue='queue')
