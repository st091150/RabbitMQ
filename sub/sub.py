import pika
import json
import time
from functools import reduce
import operator

def Connect(params) -> bool:
    global connection, channel
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
    except Exception:
        return False
    return True

def ADD(list):
    return sum(list)

def SUB(list):
    return reduce(operator.__sub__, list)

def MUL(list):
    return reduce(operator.__mul__, list)

def DIV(list):
    return reduce(operator.__truediv__, list)

operations = {"ADD" : ADD, "SUB" : SUB, "MUL" : MUL, "DIV" : DIV}


def callback(ch, method, properties, body):
    message = json.loads(body)
    if "data" and "operation" in message:
        print(f" [x] Received (data : {message['data']}, operation : {message['operation']})")
    try:
        if message["operation"] in operations.keys():
            result = operations[message["operation"]](message["data"])
            print(f"Result: {result}")
        else:
            raise Exception("Unknown operation")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error while processing message : {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)



params = pika.URLParameters('amqp://user:psw@rabbitmq/')
connection = None
channel = None

while not Connect(params):
    time.sleep(1)
    print("Reconnect\n")
    continue

channel.queue_declare(queue='queue_1', durable=True, arguments={
"x-dead-letter-exchange": '', "x-dead-letter-routing-key": 'DLQ_queue_1'})

channel.basic_consume(queue='queue_1', on_message_callback=callback, auto_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()