import pika
import os
import sys
import io
import csv
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from docx import Document
import PyPDF2
import json

rabbitmq_host = 'rabbitmq'
rabbitmq_queue = 'fileUploadQ'

minio_client = Minio(
    "minio-headless-svc:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False  
)

def get_file_from_minio(bucket_name, file_path):
    try:
        response = minio_client.get_object(bucket_name, file_path)
        file_data = BytesIO(response.read())
        print(f"File downloaded to memory")
        return file_data
    except S3Error as err:
        print(f"MinIO error: {err}")
        return None
    
def process_file(file_data, file_path):
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".docx":
            text = extract_docx(file_data)
        elif file_ext == ".pdf":
            text = extract_pdf(file_data)
            print(text)
        else:
            raise ValueError("Unsupported file format")
        
        return split_text(text)
    
    finally:
        file_data.close()

def extract_docx(file_data):
    document = Document(file_data)
    content = []
    for paragraph in document.paragraphs:
        content.append(paragraph.text)
    return "\n".join(content)

def extract_pdf(file_data):
    pdf_reader = PyPDF2.PdfReader(file_data)
    content = []
    for page in pdf_reader.pages:
        content.append(page.extract_text())
    return "\n".join(content)

def split_text(text):
    return text.split()

def send_to_queue(tokenized_data, file_path):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='MongoSaveQUEUE', exchange_type='fanout')
    
    message = {
        "file_path": file_path,
        "tokenized_data": tokenized_data
    }

    channel.basic_publish(exchange='MongoSaveQUEUE', routing_key='', body=json.dumps(message))

    print(f" [x] Sent tokenized data for file {file_path} to queue")
    connection.close()

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='FileUploadQUEUE', exchange_type='fanout')

    channel.queue_declare(queue=rabbitmq_queue)
    channel.queue_bind(exchange='FileUploadQUEUE', queue=rabbitmq_queue)

    def callback(ch, method, properties, body):
        try:
            file_info = body.decode()
            bucket_name = file_info.split("/")[1] 
            file_path = os.path.join(*file_info.split("/")[2:])
            file_data = get_file_from_minio(bucket_name, file_path)

            if file_data:
                tokenized_text = process_file(file_data, file_path)
                if tokenized_text:
                    send_to_queue(tokenized_text, file_path)
                    ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e :
                print(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True) 

    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False)
    print('Waiting for messages...')
    channel.start_consuming()


if __name__ == "__main__":
    consume_from_queue()
