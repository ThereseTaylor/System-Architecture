import json
import time
from collections import defaultdict
import sys
import pika
import time
from pymongo import MongoClient
from datetime import datetime  
from bson import ObjectId

rabbitmq_host = 'rabbitmq'
rabbitmq_queue = 'aggregatorQ'

aggregated_results = defaultdict(list)
#MAX_RETRIES = 3

def process_message(doc_id, result, analysis):
    aggregated_results[doc_id].append({analysis: result})
    print(f"Doc ID: {doc_id}, Aggregated Results: {aggregated_results[doc_id]}")
    sys.stdout.flush()

    if len(aggregated_results[doc_id]) == 5:
        return finalize_aggregation(doc_id)  
    return True

def finalize_aggregation(doc_id):
    final_result = {
        "doc_id": doc_id,
        "results": aggregated_results[doc_id]  
    }

    save_successful = save_to_mongodb(doc_id, final_result)
    
    if save_successful:
        send_to_email(doc_id)
        del aggregated_results[doc_id]
        return True
    else:
        print(f"MongoDB save failed for doc_id: {doc_id}. Requeueing message.")
        sys.stdout.flush()
        return False 

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            doc_id = message['doc_id']
            result = message['result']
            analysis = message['analysis']

            ch.basic_ack(delivery_tag=method.delivery_tag)  

            processing_successful = process_message(doc_id, result, analysis)
            
            if processing_successful is False:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  

    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()

def send_to_email(result):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='emailQ')

    message = json.dumps(result)
    channel.basic_publish(exchange='', routing_key='emailQ', body=message)

    connection.close()

def save_to_mongodb(doc_id, data):
    try:
        # MongoDB Setup
        client = MongoClient("mongodb://mongodb-headless-svc:27017/")
        db = client['tokenizer_db']
        collection = db['tokenizer_output']
        # Find the document by doc_id
        doc = collection.find_one({"_id": ObjectId(doc_id)})

        if doc:
            # Update the existing document with new results
            for result in data["results"]:
                service_name = list(result.keys())[0]
                collection.update_one(
                    {"_id": ObjectId(doc_id)},
                    {
                        "$push": {
                            "results": {service_name: result[service_name]}
                        },
                        "$set": {
                            "last_updated": datetime.now()
                        }
                    }
                )
            print(f"Result updated for document with doc_id 1: {doc_id}")
            sys.stdout.flush()
            return True
        else:
            print(f"No document found with doc_id 12: {doc_id}")
            sys.stdout.flush()
            return False
        
    except Exception as e:
        print(f"Error saving data to MongoDB 123: {e}")
        sys.stdout.flush()
        return False

if __name__ == "__main__":
    consume_from_queue()

