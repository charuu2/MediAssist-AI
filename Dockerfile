# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port (optional)
EXPOSE 5000

# Use Render's PORT environment variable
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app --workers=1 --threads=2"]
