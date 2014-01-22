#!/usr/bin/env python

import sys
import pika
import time


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
        with open("log.txt", "a") as f:
            sys.write(f, self.__dict__)


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

    def send(self, exchange='', routing_key='', body=None, properties=None,
             mandatory=False, immediate=False):
        # Create a channel
        channel = self.connection.channel()

        # Send the message
        channel.basic_publish(exchange=exchange, routing_key=routing_key,
                              body=body, properties=properties,
                              mandatory=mandatory, immediate=immediate)

        # Close the channel
        channel.close()

    def receive(self, callback, queue=''):
        # Create a channel
        channel = self.connection.channel()

        # Receive a message
        channel.basic_consume(callback, queue=queue, no_ack=True)

        # Close the channel
        # channel.close()

    def rpc(self, exchange='', routing_key='', body=None, properties=None,
            mandatory=False, immediate=False, timeout=60):
        # Create a channel
        channel = self.connection.channel()

        # Create a temporary auto-delete queue
        queue = channel.queue_declare(exclusive=True, auto_delete=True,
                                      durable=False).method.queue

        # Set up message properties
        if properties is None:
            properties = pika.spec.BasicProperties()
        properties.reply_to = queue

        # Send the message
        self.send(exchange=exchange, routing_key=routing_key, body=body,
                  properties=properties, mandatory=mandatory,
                  immediate=immediate)

        # Mark the start time
        start = time.time()

        # Create the callback object
        callback = AmqpRpcCallback()

        # Start consumer
        channel.basic_consume(callback.on_receive, no_ack=True)

        # Wait until we receive a message or we reach the timeout
        while not callback.received and time.time() < start + timeout:
            # Force data events to run
            channel.connection.process_data_events()

            # Wait a bit
            time.sleep(0.1)

        # Reached the timeout, close the channel
        channel.close()

        # Check whether we got a response
        if callback.received:
            return callback.method, callback.header, callback.body

        return None

    def close(self):
        self.connection.close()
        self.connection = None
