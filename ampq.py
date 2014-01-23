import pika


class AmqpRpcCallback:
    def __init__(self):
        self.received = False
        self.method = None
        self.header = None
        self.body = None

    def on_receive(self, channel, method, header, body):
        self.received = True
        self.method = method
        self.header = header
        self.body = body


class AmqpConnection:
    def __init__(self, host=None, port=5672, virtual_host='/', username=None,
                 password=None):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password

        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=pika.credentials.PlainCredentials(
                username=self.username, password=self.password)))

    def receive(self, callback, queue=''):
        # Create a channel
        channel = self.connection.channel()

        # Receive a message
        channel.basic_consume(callback, queue=queue, no_ack=True)

        # Contiume consuming
        channel.start_consuming()

    def close(self):
        self.connection.close()
        self.connection = None
