# dockerfile, Image, Container
FROM python:3.12

WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y iputils-ping && apt-get clean

# Find ping and show where it is
RUN find / -name "ping" -type f 2>/dev/null && echo "=== PING LOCATIONS ===" && which ping && echo "=== PATH ===" && echo $PATH

# Copy the actual application file
COPY app.py /app/app.py

# Run the application
CMD ["python", "app.py"]
