FROM python:3.PYTHON_VERSION_MINOR

# Create a working directory
WORKDIR /app

# Copy the contents to the container
COPY PROJECT_NAME /app/PROJECT_NAME

# Set the working directory to the target folder
WORKDIR /app/PROJECT_NAME

# compile and pack project
RUN python3 -m pip install linpgtoolbox
RUN linpgtb -c .
RUN linpgtb -p