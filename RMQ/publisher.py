from consumer import PikaClient
from homalogger import logger
import json


class PikaPublisher(PikaClient):
    """
    Class used for publishing messages to message bus

    Attributes
    ----------
    dl_queue: str
        name of the deadletter queue
    exchange: str
        name of the exchange that we want to publish to
    queue: str
        name of the response queue
    queue_ttl: int
        time to live for messages in response queue before they are moved to deadletter queue
    """
    def __init__(self, env_conf, io_loop):
        self.dl_queue = env_conf["DEAD_LETTER_QUEUE"]
        self.exchange = 'l3vpn-ingestion'
        self.queue = env_conf["RESPONSE_QUEUE"]
        self.queue_ttl = env_conf["QUEUE_TTL"]
        super().__init__(env_conf, io_loop)

    def on_queue_declare_ok(self, method_frame):
        """
        callback function that is called when a queue is created for first time or is identified that it exists

        Parameters
        ----------
        method_frame
            Method frame associated with the created queue

        """
        logger.info('RabbitMQ queue - {} exists or created'.format(self.queue))

    def on_channel_open(self, channel):
        """
        callback function that is called when an RMQ channel is opened

        Parameters
        ----------
        channel
            a reference to the channel object that is opened

        """
        logger.info('RabbitMQ publisher channel opened')
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)

        self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')

        self.channel.queue_declare(self.queue, passive=False, durable=True,
                                   callback=self.on_queue_declare_ok)
        self.channel.queue_bind(self.queue, self.exchange, routing_key=self.queue)
        # Declare and bind dead-letter queue
        self.channel.queue_declare(self.dl_queue, passive=False, durable=True)
        self.channel.queue_bind(self.dl_queue, self.exchange, routing_key=self.dl_queue)


    def publish(self, msg):
        """
        function that publishes a message to response queue on message bus

        Parameters
        ----------
        msg: dict
            dictionary containing the message that we want to publish to message bus

        """
        if self.channel is None:
            self.connect()

        logger.info("publishing to message bus: \n{}".format(json.dumps(msg, indent=4)))
        msg_bytes = json.dumps(msg).encode('UTF-8')
        self.channel.basic_publish(exchange=self.exchange, routing_key=self.queue, body=msg_bytes, mandatory=True)



