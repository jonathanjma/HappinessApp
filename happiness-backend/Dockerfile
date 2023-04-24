FROM python:3.8.0

# Copy local code to the container image
COPY . /app

# Sets the working directory
WORKDIR /app

# Upgrade PIP
RUN pip install --upgrade pip

# Install python libraries from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set $PORT environment variable
ENV PORT 8080


# Run the web service on container startup
CMD flask db upgrade
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 happiness_backend:app