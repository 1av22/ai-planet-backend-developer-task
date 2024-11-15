# ai-planet-backend-developer-task
- To start the services you should have ```Docker Desktop``` installed.
- After cloning the project move inside the project root folder and type ```docker-compose up --build```.
- The services should start.
- The api is ready to serve in ```loacalhost:8000```.
- We have the following API endpoints for user management that uses JWT for access token:
  - **user register**:```localhost:8000/auth/register```.
  - **user login**:```localhost:8000/auth/login```.
  - **get current user**:```localhost:8000/auth/register```.
  - **logout user**:```localhost:8000/auth/logout```.
- We have the following API endpoints for file management that saves file to S3 bucket:
  - **upload files**:```localhost:8000/files/upload```.
  - **download files**:```localhost:8000/files/download/{file_name}```.
  - **list all files**:```localhost:8000/auth/list```.
  - **delete files**:```localhost:8000/files/delete/{file_name}```.
- We have the following API endpoints for RAG Agent:
  - **chat with RAG**:```localhost:8000/rag/chat```.

## Technologies used:
- FastAPI: For creating the API
- JWT: For creating session tokens and authentication.
- PostgreSQL: For storing the user data and the files metadata.
- Unstructured: For parsing the files.
- Spacy: For creating the embeddings.
- OpenAI: For the answering of the questions.
- NextJs: For the frontend.
- Docker: Containerization.

In the end I would like to say thankyou to the AI Planet team for providing me with such an amazing opportunity at attempting the task for backend engineer. because of it I got familiarized with many new technologies and methods to create a robust RAG GenAI application. I was not able to complete the task fully due to time constrains but I hope that my task is considered.
Thankyou.
