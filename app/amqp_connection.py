import pika

from app import app

amqp_url = app.config['AMQP_URI']
amqp_params = pika.ConnectionParameters(
    host=amqp_url.hostname,
    virtual_host=amqp_url.path[1:],
    credentials=pika.PlainCredentials(
        amqp_url.username,
        amqp_url.password,
    ))

def get_amqp_connection():
    return pika.BlockingConnection(amqp_params)

def test_amqp_connection():
    connection = get_amqp_connection()
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='hello') # Declare a queue
    # send a message
    channel.basic_publish(exchange='', routing_key='hello', body='Hello CloudAMQP!')
    print " [x] Sent 'Hello World!'"

    # create a function which is called on incoming messages
    def callback(ch, method, properties, body):
      print " [x] Received %r" % (body)

    # set up subscription on the queue
    channel.basic_consume(callback,
        queue='hello',
        no_ack=True)

    channel.start_consuming() # start consuming (blocks)

    connection.close()

if __name__ == '__main__':
    test_amqp_connection()
