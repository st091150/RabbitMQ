import pika
import time
import json
import random

def Connect(params,) -> bool:
    global connection, channel
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
    except Exception:
        return False
    return True
    


operations = ["ADD", "SUB", "MUL", "DIV"]

params = pika.URLParameters('amqp://user:psw@rabbitmq/')
connection = None
channel = None


while not Connect(params):
    time.sleep(1)
    print("Reconnect\n")
    continue

channel.queue_declare(queue='DLQ_queue_1', durable=True)

channel.queue_declare(queue='queue_1', durable=True, arguments={
"x-dead-letter-exchange": '', "x-dead-letter-routing-key": 'DLQ_queue_1'})

try:
    while True:
        message = json.dumps({"data": random.sample(range(0, 1000), random.randint(1, 10)), "operation": operations[random.randint(0, 3)]})
        channel.basic_publish(exchange='',
                            routing_key='queue_1',
                            body=message)

        print(f" [x] Sent {message}")
        time.sleep(1)
except KeyboardInterrupt:
    connection.close()