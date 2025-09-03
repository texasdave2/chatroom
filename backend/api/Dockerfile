# Base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app


# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application as a module
#CMD ["/usr/local/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]


