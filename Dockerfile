# Use the official Python image from the Docker Hub
FROM python:3.9-slim-buster


# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY ./requirements.txt /app

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose port 5000
EXPOSE 5000
ENV FLASK_APP=app.py
# Command to run the Flask application
CMD ["flask", "run", "--host", "0.0.0.0"]
