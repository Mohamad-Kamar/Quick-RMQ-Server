from pika_client import PikaClient
from homalogger import logger
import json
import datetime
import hashlib
import time


class PikaConsumer(PikaClient):
    """
    Class used for consuming messages from message bus
    Attributes
    ----------
    dispatcher: object
        reference to an instance of the dispatcher object used for routing
        incoming request to the appropriate workflow
    """
    def __init__(self, env_conf, io_loop,publisher):
        super().__init__(env_conf, io_loop)
        self.publisher = publisher

    def on_channel_open(self, channel):
        """
        callback function that is called when an RMQ channel is opened

        Parameters
        ----------
        channel
            a reference to the channel object that is opened

        """
        logger.info('RabbitMQ consumer channel opened')
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)

        channel.basic_consume(on_message_callback=self.on_message, queue=self.env_conf["REQUEST_QUEUE"], auto_ack=False)
        logger.info("RabbitMQ Consumer callback registered")

    def on_message(self, channel, basic_deliver, properties, body):
        """
        Callback function that is called when a message appears on message bus

        Parameters
        ----------
        channel: object
            a reference to the channel object that message was published on that
        basic_deliver
            reference to the object that controls the acknowledgement
            behavior after consuming a message from massage bus
        properties: object
            reference to an object containing properties of the message on message bus
        body: bytearray
            bytearray representation of the message on message bus

        Returns
        -------

        """
        logger.info("Consumed Message from Request Queue")
        payload = json.loads(body.decode('utf-8'))
        # payload = body
        logger.info("Received request on message bus:\n{}".format(json.dumps(payload, indent=4)))
        received_id = payload["id"]
        new_payload = {}
        new_payload["correlationId"] = received_id
        service_id = payload["request-characteristics"]["url-query-parameters"][0]["value"]
        new_payload["eventTime"] = str(datetime.datetime.now())
        new_payload["eventId"] = self._generate_event_id()
        new_payload["event"] = {
                "service":{
                    "id":service_id,
                    "href":"/l3vpn",
                    "status":"success"
                }
        }

        sample_request = {
            "correlationId":"some_id",
            "eventTime":"time",
            "eventId":"id",
            "event":{
                "service":{
                    "id":"<service-id>",
                    "href":"/l3vpn",
                    "status":"success"
                }                
            }
        }
        self.publisher.publish(new_payload)
        self.channel.basic_ack(basic_deliver.delivery_tag)



    def _generate_event_id(self):
        """
        Function used to Generate an event id for notifications being sent to northbound

        Returns
        --------
        str
            even id to be used in callback to northbound system
        """
        hash_object = hashlib.sha1()
        hash_object.update(str(time.time()).encode('utf-8'))
        return str(hash_object.hexdigest()[:10])
