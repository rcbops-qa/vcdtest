#!/usr/bin/env python
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu import Queue
from kombu.utils.debug import setup_logging


TASK_QUEUES = [Queue('queue')]

CREDS = {
    'user': 'guest',
    'pass': 'guest',
    'port': '5672',
    'host': 'localhost',
    'vhost': '/'
}

logger = get_logger(__name__)


class ProcessFailure(Exception):
    pass


def process_task(body, message):
    try:
        # Execute the code.
        print(body)
    except Exception as exc:
        logger.error('task raised exception: %r', exc)
    else:
        message.ack()


class Worker(ConsumerMixin):
    """Rip messages from Queue and then consume them."""

    def __init__(self, connection):
        """Open a worker connection for a consumer."""

        self.connection = connection

    def get_consumers(self, Consumer, channel):
        """Get the consumer."""

        return [Consumer(queues=TASK_QUEUES,
                         accept=['json'],
                         callbacks=[process_task])]


if __name__ == '__main__':
    setup_logging(loglevel='INFO', loggers=[''])
    setup_connection = 'amqp://%(user)s:%(pass)s@%(host)s:%(port)s' % CREDS

    with Connection(setup_connection) as conn:
        try:
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
            raise SystemExit('Process Killed.')
