# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    git \
    && apt-get clean
# Step 4: Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install wheel setuptools pip --upgrade 
RUN pip install git+https://github.com/ageitgey/face_recognition_models --verbose
RUN pip install git+https://github.com/davisking/dlib.git@master

RUN pip install Flask
RUN pip install flask_cors
RUN pip install pillow
RUN pip install numpy
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt
RUN pip install python-dotenv

# Step 5: Expose the Flask port
EXPOSE 5002

# Step 6: Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/automatic-time-379113-5440df4089b9.json"
ENV FLASK_ENV=development  

# Step 7: Run the application
CMD ["flask", "run"]
