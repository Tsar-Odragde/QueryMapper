# Base image
FROM python:3.9-slim

# Install ODBC driver dependencies
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Set working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 3000
EXPOSE 3000

# Command to run the application on port 3000
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:3000"]
