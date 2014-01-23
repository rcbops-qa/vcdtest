#!/usr/bin/env python

import argh
from ampq import AmqpConnection


def callback(channel, method, header, body):
    print body


def consume(host, username, password, virtual_host, queue):
    connection = AmqpConnection(host=host, username=username,
                                password=password, virtual_host=virtual_host)
    connection.receive(callback, queue=queue)

argh.dispatch_command(consume)
