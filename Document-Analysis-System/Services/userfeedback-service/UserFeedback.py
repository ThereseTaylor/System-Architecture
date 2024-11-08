import pymongo
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import pika
from minio import Minio
from minio.error import S3Error
import os
import sys
from io import BytesIO
from bson import ObjectId

# RabbitMQ configuration
rabbitmq_host = 'rabbitmq'
rabbitmq_queue = 'emailQ'

# Get credentials from environment variables
access_key = os.getenv('MINIO_ACCESS_KEY')
secret_key = os.getenv('MINIO_SECRET_KEY')

# Ensure credentials are set
if not access_key or not secret_key:
    raise EnvironmentError("MinIO access_key and/or secret_key environment variables are not set.")

# Initialize MinIO client
minio_client = Minio(
    "minio-headless-svc:9000",  # Replace with your MinIO server URL
    access_key=access_key,
    secret_key=secret_key,
    secure=False  # Set to True if using HTTPS
)

bucket_name = "feedback"
try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")
except S3Error as e:
    print(f"Error checking or creating bucket: {e}")

# MongoDB configuration
client = pymongo.MongoClient("mongodb://mongodb-headless-svc:27017/")
db = client["tokenizer_db"]
collection = db["tokenizer_output"]
    
# Function to retrieve the "results" section and "file_path" from MongoDB by unique identifier
def retrieve_results_from_mongodb(document_id):
    try:
        # Strip any extra quotes or whitespace from the document ID
        document_id = document_id.strip('\"\' ')
        
        # Convert the string ID to an ObjectId for querying MongoDB
        object_id = ObjectId(document_id)

        # Query for the specific document using the document's unique identifier and include "results" and "file_path"
        document = collection.find_one({"_id": object_id}, {"results": 1, "file_path": 1, "_id": 0})
        if document and "results" in document and "file_path" in document:
            return document
        else:
            print(f"No 'results' or 'file_path' found in document with ID: {document_id}")
            sys.stdout.flush()
            return None
    except Exception as e:
        print(f"Error retrieving data from MongoDB: {e}")
        sys.stdout.flush()
        return None

# Function to generate a PDF report containing only the "results" section and file name
def generate_pdf_report(document):
    try:
        buffer = BytesIO()  # Create a buffer for the PDF content
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []  # Store all the document elements
        
        # Define styles
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        title_style = styles['Title']
        heading_style = styles['Heading2']
        
        # Add title
        title = Paragraph("SimiLabs Document Analysis Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))  # Add some space after the title
        
        # Add file name section
        file_path = document.get("file_path", "Unknown")
        file_name = os.path.basename(file_path)
        file_name_paragraph = Paragraph(f"<b>File Name:</b> {file_name}", normal_style)
        elements.append(file_name_paragraph)
        elements.append(Spacer(1, 12))  # Space after the file name
        
        # Add the "Results" section title
        results_title = Paragraph("Results:", heading_style)
        elements.append(results_title)
        elements.append(Spacer(1, 12))  # Space after the title
        
        # Combine all the results into a single string
        results = document.get("results", [])
        result_strings = []
        
        for result in results:
            for key, value in result.items():
                result_strings.append(f"<b>{key}:</b> {value}")
        
        # Create a paragraph for the combined results
        combined_results = "<br />".join(result_strings)
        results_paragraph = Paragraph(combined_results, normal_style)
        elements.append(results_paragraph)
        
        # Build the PDF
        pdf.build(elements)
        
        # Return the PDF as a BytesIO object
        buffer.seek(0)  # Move to the beginning of the buffer
        return buffer
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        sys.stdout.flush()
        return None

def send_to_bucket(pdf_buffer, original_file_name):
    pdf_filename = f"SimiLabs_Report: {original_file_name}"
    try:
        minio_client.put_object(
            bucket_name,
            pdf_filename,  
            pdf_buffer,
            length=-1, 
            part_size=10 * 1024 * 1024,
        )
    except S3Error as e:
        return {"error": str(e)}

# Function for consumer service
def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)

    def callback(ch, method, properties, body):
        try:
            # Decode the document ID from RabbitMQ message
            document_id = body.decode()
            print(f"Processing document ID: {document_id}")
            sys.stdout.flush()

            # Retrieve the specific document's "results" and "file_path" from MongoDB
            document = retrieve_results_from_mongodb(document_id)

            if document:
                original_file_name = os.path.basename(document["file_path"])

                pdf_buffer = generate_pdf_report(document)

                if pdf_buffer:
                    send_to_bucket(pdf_buffer, original_file_name)
                else:
                    print("Failed to generate PDF.")
                    sys.stdout.flush()
            else:
                print("No 'results' or 'file_path' data to report.")
                sys.stdout.flush()

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {e}")
            sys.stdout.flush()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()

def main():
    consume_from_queue()

if __name__ == "__main__":
    main()
