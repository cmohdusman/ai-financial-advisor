FROM python:3.13.5-slim

WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make script executable
RUN chmod +x start.sh

# Expose HF-required port
EXPOSE 7860

# Start app
CMD ["./start.sh"]