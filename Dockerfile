# Use the official Python image as the base image.
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
# This step will re-run only if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code.
# This step will re-run if any source code changes.
COPY . .

# The port your container will listen on. Cloud Run expects this to be
# the port specified by the PORT environment variable.
ENV PORT 8080

# Start the web server with Gunicorn.
# The `app:app` part points to your Flask app instance.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]