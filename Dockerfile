# Base image
FROM python:3.9-slim

# Install necessary system packages and ODBC dependencies
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    apt-transport-https \
    unixodbc-dev

# Add Microsoft’s repository for SQL Server ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 3000
EXPOSE 3000

# Start application with Gunicorn
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:3000"]
