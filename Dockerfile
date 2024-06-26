# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the requirements file to install dependencies
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY endpoint.py ./
COPY model.py ./
COPY artifacts/model_60000.pt ./artifacts/model_60000.pt

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Run Gunicorn to serve the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "endpoint:app"]
