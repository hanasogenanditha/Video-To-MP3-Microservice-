# Video to MP3 Microservice

A scalable microservices-based video-to-MP3 processing system built using Python (Flask).  
Users can securely upload video files and receive converted MP3 audio files via email through an asynchronous background processing pipeline.

---

## Tech Stack

1. Backend: Python (Flask)  
2. Authentication: JWT (JSON Web Tokens)  
3. Messaging Queue: RabbitMQ  
4. Media Processing: FFmpeg  
5. File Storage: MongoDB (GridFS)  
6. Database: MySQL  
7. Containerization: Docker  
8. Orchestration: Kubernetes  

---

## Architecture Overview

This project follows a distributed, event-driven microservices architecture designed for scalability, fault isolation, and non-blocking media processing.

Each service is independently deployable and communicates through REST APIs and RabbitMQ, ensuring loose coupling and horizontal scalability.

---

### API Gateway

1. Acts as the single entry point for all client requests  
2. Handles routing to internal services  
3. Verifies JWT tokens before forwarding requests  
4. Manages login, upload, and download endpoints  
5. Prevents direct exposure of internal services  

---

### Auth Service

1. Handles user registration and login  
2. Stores user credentials securely in MySQL  
3. Generates and validates JWT tokens  
4. Enables stateless authentication across services  

---

### Converter Service

1. Consumes video processing jobs from RabbitMQ  
2. Uses FFmpeg to extract audio from uploaded video files  
3. Stores generated MP3 files in MongoDB GridFS  
4. Runs asynchronously to prevent blocking user requests  
5. Can be horizontally scaled to handle higher workloads  

---

### Notification Service

1. Listens for completed conversion events  
2. Sends email notifications to users with download links  
3. Is decoupled from the conversion logic using RabbitMQ  
4. Ensures reliable user communication without affecting processing flow  

---

## System Workflow

1. User registers or logs in via the API Gateway.  
2. Auth Service validates credentials and issues a JWT token.  
3. User uploads a video file through the Gateway.  
4. A job message is published to RabbitMQ.  
5. Converter Service consumes the message and extracts audio using FFmpeg.  
6. Converted MP3 file is stored in MongoDB GridFS.  
7. Notification Service sends an email to the user with the download link.  

---

## System Design Highlights

1. Event-driven architecture using RabbitMQ  
2. Fully asynchronous processing pipeline  
3. Stateless authentication using JWT  
4. Scalable file storage with MongoDB GridFS  
5. Secure credential storage using MySQL  
6. Containerized services using Docker  
7. Kubernetes Deployments, Services, ConfigMaps, and Secrets    
9. Clear separation of concerns across services  

---


## Security

1. JWT-based authentication  
2. Secure configuration using Kubernetes Secrets  
3. Internal service-to-service communication  

---

## Key Features

1. Non-blocking media processing  
2. Asynchronous job handling  
3. Scalable microservices architecture  
4. Secure authentication and authorization   

---

## Future Improvements

1. Monitoring and logging integration  
2. CI/CD pipeline setup  
3. Rate limiting and API throttling  
4. Retry mechanisms for failed conversions  
5. Cloud deployment (AWS / GCP / Azure)  