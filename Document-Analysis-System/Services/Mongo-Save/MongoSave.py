import pika
import pymongo 
import json
from datetime import datetime
import uuid

rabbitmq_host = 'rabbitmq'
mongo_save_queue = 'mongoSaveQ'
client = pymongo.MongoClient("mongodb://mongodb-headless-svc:27017/")  # MongoDB service
db = client["tokenizer_db"]
collection = db["tokenizer_output"]

def save_to_mongodb(data):
    try: 
        # Insert data into MongoDB
        result = collection.insert_one(data)
        return result.inserted_id
    except Exception as e:
        print(f"Error saving data to MongoDB: {e}")
    finally:
        # Close MongoDB connection
        client.close()

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    channel.exchange_declare(exchange='MongoSaveQUEUE', exchange_type='fanout')
    channel.queue_declare(queue=mongo_save_queue)
    channel.queue_bind(exchange='MongoSaveQUEUE', queue=mongo_save_queue)

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            file_path = message['file_path']
            tokenized_data = message['tokenized_data']

            # Save to MongoDB
            doc = {
                "file_path": file_path,
                "tokenized_data": tokenized_data,
                "uuid": str(uuid.uuid4()),  # Unique identifier generated for the document
                "timestamp": datetime.now(),
            }

            try:
                id = save_to_mongodb(doc)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                send_to_microservices(f"{id}|{tokenized_data}")
            except Exception as e:
               print(f"Failed to save to MongoDB: {e}")

        except Exception as e :
            print(f"Error processing message: {e}")
            # Optionally reject and requeue the message for later retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=mongo_save_queue,on_message_callback=callback,auto_ack=False)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
def send_to_microservices(payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    
    exchange_name = 'MicroserviceFanoutExchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    channel.basic_publish(
        exchange=exchange_name,
        routing_key='',  
        body=payload
    )

    connection.close()

if __name__ == "__main__":
    consume_from_queue()


