FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy the application code to the working directory
COPY /app .

# Expose the port on which the application will run
EXPOSE 8000

# Run the FastAPI application using uvicorn server
#CMD ["uvicorn", "fastapi:app", "--host", "0.0.0.0", "--port", "8080"]