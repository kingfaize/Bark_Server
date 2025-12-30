FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package in editable mode for configuration access
RUN pip install -e .

# Expose ports for FastAPI (8080) and Streamlit (8501)
EXPOSE 8080
EXPOSE 8501

# Default command starts the Streamlit dashboard
# (Which can then start the server process)
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
