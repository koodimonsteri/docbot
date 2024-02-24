FROM python:3.9-slim

ENV PYHTONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY /app .

EXPOSE 8000

# Run the FastAPI application using uvicorn server
#CMD ["uvicorn", "fastapi:app", "--host", "0.0.0.0", "--port", "8080"]