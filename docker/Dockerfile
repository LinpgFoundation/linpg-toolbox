FROM python:3.PYTHON_VERSION_MINOR

# Create a working directory
WORKDIR /app

# Copy the contents of the linpgtoolbox folder to the container
COPY linpg-toolbox /app/linpgtoolbox

# Set the working directory to the linpgtoolbox folder
WORKDIR /app/linpgtoolbox

# Run cli.py
RUN python3 -m linpgtoolbox.cli -c .
RUN python3 -m linpgtoolbox.cli -p