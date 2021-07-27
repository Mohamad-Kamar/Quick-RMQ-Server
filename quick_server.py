from envyaml import EnvYAML
from consumer import PikaConsumer
from publisher import PikaPublisher

import tornado.ioloop


io_loop = tornado.ioloop.IOLoop.current()


env_conf = EnvYAML('./env.yaml')
rmq_publisher = PikaPublisher(env_conf=env_conf, io_loop=io_loop)
rmq_publisher.connect()

rmq_consumer = PikaConsumer(env_conf=env_conf, io_loop=io_loop, publisher=rmq_publisher)
rmq_consumer.connect()
io_loop.start()

