import pika

from app import app

ampq_url = app.config['AMPQ_URI']
ampq_params = pika.ConnectionParameters(
    host=ampq_url.hostname,
    virtual_host=ampq_url.path[1:],
    credentials=pika.PlainCredentials(
        ampq_url.username,
        ampq_url.password,
    ))

def get_ampq_connection():
    return pika.BlockingConnection(ampq_params)

def test_ampq_connection():
    connection = get_ampq_connection()
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
    test_ampq_connection()
