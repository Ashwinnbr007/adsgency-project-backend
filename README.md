# Adsgency Backend Project

Use the app to create books, reviews and comments on reviews.

## Postman Collection

The api documentation as well as the postman collection for all endpoints : 
[Postman Collection](https://solar-astronaut-555802.postman.co/workspace/adsgency~c295e425-153c-4689-901a-8fcebe007c80/overview).

## UML Diagram

[UML Diagram](https://drive.google.com/file/d/1sbZFf0UFpqHRqhZB2u9eWyIXdbDQat7L/view?usp=sharing).

## Getting Started

### Prerequisites

Make sure you have the following installed:
- Python (3.9 or higher)
- Docker (optional, for containerization)

### Installation

You can either run the app as a docker image (If you have docker installed) or you can install locally

#### Local Setup 

1. Clone the repo
2. Create a venv in your directory
    - ```python -m venv venv```
3. Activate the venv
    - ```source venv/bin/activate```
4. Install the dependencies
    - ```pip install -r requirements.txt```

#### Docker Setup 

1. Clone the repo
2. Install and run using docker compose 
    - ```docker-compose up --build```

### ENV

Before you run the app, make sure to add the following env variables to .env in the root of the project

- ```MONGO_USERNAME=adsgency-project```
- ```MONGO_PASSWORD=4GtXmRvBXczcoLqh```
- ```MONGO_URI=mongodb+srv://adsgency-project:4GtXmRvBXczcoLqh@adsgency-project.6h1lfjc.mongodb.net/```
- ```SESSION_SECRET=e5cf878c913ba673b187c8af6ed007da```
- ```JWT_SECRET=bba11ebc9e97083b4e2a9856a146c3c0```

These env files will allow you to connect to the database on MongoDB cloud servers.