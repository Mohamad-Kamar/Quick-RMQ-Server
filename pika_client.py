import pika
import ssl
from pika.adapters import tornado_connection
from pika.exceptions import AMQPConnectionError, AuthenticationError, ProbableAuthenticationError
from homalogger import logger


class PikaClient(object):
    """
    Based class to support helper functions for consumer and publisher classes

    Attributes
    ----------
    io_loop: object
        a reference to the instance of io_loop handling queue read/write operations
    env_conf: dict
        a dictionary containing configuration variables of the application
    connection
        a reference to the connection object
    channel
        a reference to the channel associated with this PikaClient instance
    """
    def __init__(self, env_conf, io_loop):
        self.io_loop = io_loop
        self.env_conf = env_conf

        self.connection = None
        self.channel = None

        logger.info("Pika Client Created successfully")

    def connect(self):
        """
        function to establish connection to RabbitMQ channel
        """
        try:
            cred = pika.PlainCredentials(self.env_conf['RABBIT_USER'], self.env_conf['RABBIT_PASSWORD'])

            params = pika.ConnectionParameters(host=self.env_conf['RABBIT_HOST'], port=self.env_conf['RABBIT_PORT'], credentials=cred)

            self.connection = tornado_connection.TornadoConnection(
                params, custom_ioloop=self.io_loop, on_open_callback=self.on_connected)

            self.connection.add_on_open_error_callback(self.error)
            self.connection.add_on_close_callback(self.on_connection_closed)
            logger.info("Connect method ended")
        except Exception as e:
            logger.exception(e)

    def on_connected(self, conn):
        """
        callback function that is called when a connection to channel is established

        Parameters
        ----------
        conn
            a reference to the object representing connection to the channel
        """
        logger.info("RabbitMQ Connection Opened")
        self.connection = conn
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """
        callback function that is called when a channel is opened

        Parameters
        ----------
        channel
            a reference to the channel object associated with this PikaClient instance
        """
        self.channel = channel
        # move this to the on_channel_open methods of consumer and publisher
        self.channel.add_on_close_callback(self.on_channel_closed)

    def error(self, conn, reason):
        """
        callback function that is called when there is an error in establishing connection to RMQ channel

        Parameters
        ----------
        conn
            reference to the connection object for communicating with RMQ channel
        reason: str
            reason for failure in connection establishment

        """
        logger.error('Connection failed to establish: Reason - {}'.format(reason))
        if isinstance(reason, AuthenticationError) or isinstance(reason, ProbableAuthenticationError):
            logger.critical('Authentication failed at RabbitMQ, not attempting to retry automatically')
        elif isinstance(reason, AMQPConnectionError):
            logger.warning('Attempting to re-establish connection in 10 seconds')
            self.connect()

    def close(self):
        """ Stop the client by closing the channel and connection. """
        logger.info('Stopping RabbitMQ channel and connection!')
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        """
        Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.
        """
        if self.channel and self.channel.is_open:
            logger.info('Closing the RabbitMQ channel')
            self.channel.close()

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self.connection and self.connection.is_open:
            logger.info('Closing the RabbitMQ connection')
            self.connection.close()

    def on_connection_closed(self, conn, reason):
        """
        callback function that is called when connection to RMQ is closed

        Parameters
        ----------
        conn
            reference to object representing connection to RMQ
        reason: str
            reason for closing of connection
        """
        self.channel = None
        self.connection = None
        logger.warning('Connection closed, reopening in 10 seconds: Reason - {}'.format(reason))
        self.io_loop.call_later(10, self.connect)

    def on_channel_closed(self, channel, reason):
        """
        callback function that is called when an RMQ channel is closed

        Parameters
        ----------
        channel
            reference to object representing RMQ channel
        reason: str
            reason for closing of channel
        """
        logger.error('RabbitMQ channel closed unexpectedly...Closing RabbitMQ connection: Reason {}'.format(reason))
        self.close_connection()