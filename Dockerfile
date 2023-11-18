# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# Copying requirements.txt first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot into the container at /app
COPY evira.py ./

# Create a non-root user and switch to it
RUN useradd -m evira
USER evira

# Run the bot when the container launches
CMD ["python", "evira.py"]
