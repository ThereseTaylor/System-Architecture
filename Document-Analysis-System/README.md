# Document Analysis System Overview

The system's aim is to efficiently handle large volumes of documents while enabling users to customise analysis features based on their specific needs, thereby enhancing decision-making processes, and driving innovation within the education sector. 

The system follows a microservice architecture, where each task is a separate service. The document is uploaded by a user (1), after which the gateway sends (2) it to be stored in a MinIO bucket (A). After a new document is uploaded it is sent (B) to the tokenizer service (4). This service extracts the text from the document and separates the words (tokens) after which it is sent to the service that saves it to the database (4), as well as to all the analytics services (5). The output of these services are then sent to the aggregator service that puts all the results related to a document together (6) and then adds this to the existing database record (C). Finally, the results, along with the file name, are retrieved to generate a report via the user feedback service (7), and this report is stored in a feedback bucket in MinIO. Each service (1-7) is deployed as a Docker container (D) within its own Kubernetes pod (E).

<img width="566" alt="ISE" src="https://github.com/user-attachments/assets/87f20756-749e-4879-8470-8a933f743061">

