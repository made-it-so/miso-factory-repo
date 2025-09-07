# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# This command will run instead of our Python script.
# It prints a single line to the log, then sleeps to keep the container running.
CMD ["sh", "-c", "echo 'DEBUG: Container has started successfully.' && sleep 3600"]