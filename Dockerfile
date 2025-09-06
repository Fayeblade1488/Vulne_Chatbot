# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Install the benchmarking package
RUN pip install -e benchmarking/

# Make port 7000 available to the world outside this container
EXPOSE 7000

# Define environment variables
ENV FLASK_APP=app/vulne_chat.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV GUARDRAILS_MODE=none
ENV PYTHONPATH=/app

# Run vulne_chat.py when the container launches
CMD ["python", "app/vulne_chat.py"]
