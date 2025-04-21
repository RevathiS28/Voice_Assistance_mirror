# Step 1: Choose the base image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file to the container
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code to the container
COPY . .

# Step 6: Expose the port (if needed, default port for your app)
EXPOSE 5000  # Modify this based on your app’s requirement

# Step 7: Set the default command to run the app
CMD ["python", "main.py"]
