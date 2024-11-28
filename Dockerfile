
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ .

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV WEB_SERVER_PORT=5000
ENV SERVER_MODE=PRODUCTION

# Run the application
CMD ["python", "app.py"]

