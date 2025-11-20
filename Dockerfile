# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Establish a working directory
WORKDIR /app_api

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app_api

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the FastAPI server when the container launches
CMD ["python", "IA_api.py"]