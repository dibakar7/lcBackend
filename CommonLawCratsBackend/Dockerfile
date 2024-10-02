# Use Python 3.10-slim as the base image
FROM python:3.10-slim

# Create the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code into the container
COPY . /app/

# Copy the .env file to the working directory
COPY .env /app/

# Expose port 8000 for the application
EXPOSE 8000

# Start the Django server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "CommonLawCratsBackend.wsgi:application"]