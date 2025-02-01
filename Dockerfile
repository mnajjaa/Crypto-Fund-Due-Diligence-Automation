FROM python:3.12-slim

# Install Node.js and npm (required for MailDev)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g maildev

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Expose ports for Django and MailDev
EXPOSE 8000  
EXPOSE 1080  
EXPOSE 1025  

# Start MailDev and Django
CMD maildev & python manage.py runserver 0.0.0.0:8000