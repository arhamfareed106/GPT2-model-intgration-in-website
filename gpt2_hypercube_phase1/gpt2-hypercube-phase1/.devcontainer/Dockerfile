FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src ./src

# Copy the configuration files
COPY configs ./configs

# Copy the scripts
COPY scripts ./scripts

# Copy the tests
COPY tests ./tests

# Set the entry point for the container
ENTRYPOINT ["bash", "./scripts/run_tests.sh"]