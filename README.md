# Bark Server (Python)

A pure Python implementation of the [Bark](https://github.com/Finb/Bark) backend server, built with **FastAPI**.

## Features

-   **Lightweight**: Built on FastAPI and Uvicorn.
-   **Database**: Uses SQLite (`bark.db`) for easy local setup.
-   **Async**: Fully asynchronous push dispatch using `httpx` (HTTP/2).
-   **Helper Scripts**: Includes tools to easily send notifications from the command line.

---

## 🚀 Quick Start (Production)

1.  **Install**: `pip install -e .`
2.  **Configure**: Update `.env` with your `BARK_DEVICE_KEY`.
3.  **Launch**: `streamlit run streamlit_app.py`
4.  **Notify**: Use the dashboard to send your first message!

## Dashboard (Streamlit)

The server includes a web-based dashboard for easy management.

### Running the Dashboard
1. Activate your virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```
2. Start the dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```
3. Open `http://localhost:8501` in your browser.

### Dashboard Features
- **Server Control**: Start/Stop the FastAPI server with a single click.
- **Send Push**: Test notifications directly from the UI without using `curl`.
- **Message History**: View a table of recent push notifications.
- **Raw Logs**: Interactive view of the system `log.log` file.

## Verbose Logging

All server events are logged verbosely to `log.log` in the project root. This includes:
- Startup/Shutdown events.
- Incoming HTTP requests and status codes.
- Push notification results and APNs feedback.
- Detailed message content (Title, Body).

## Prerequisites

-   Python 3.8+
-   A `.p8` Authentication Key from Apple (placed in `python_server/`).

## Installation

1.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    ./venv/scripts/activate  # Windows
    # source venv/bin/activate  # Linux/Mac
    ```

2.  **Install the Project**:
    This will install the server and all dependencies (FastAPI, Uvicorn, etc.).
    ```bash
    pip install -e .
    ```

## running the Server

Start the server using Uvicorn:

```bash
uvicorn python_server.main:app --host 0.0.0.0 --port 8080
```

The server will be available at `http://localhost:8080`.

## Configuration (Optional)

You can use a `.env` file to store your credentials for the helper scripts.

Create a `.env` file in the root directory:
```env
BARK_SERVER_URL=http://localhost:8080
BARK_DEVICE_KEY=your_device_key_from_the_app
```

## Usage

### 1. Using the Helper Script (Easiest)
If you have configured your `.env` file, you can send notifications instantly:

```bash
python send_message.py "Hello form Python!"
```

### 2. Using CURL
You can also send requests directly:

```bash
curl http://localhost:8080/<YOUR_KEY>/Hello%20World
```

### 3. iPhone Setup
1.  Download the **Bark** app.
2.  Add a server: `http://<YOUR_PC_IP>:8080`.
3.  Copy the generated **Device Key**.

## 🏠 Home Lab: Unraid Integration

A key use case for this server is centralizing notifications for your **Unraid** home lab.

### Setup in Unraid
1.  Go to **Settings** > **Notifications** on your Unraid WebGUI.
2.  Find the **Bark** section.
3.  Set **Agent function** to `Enabled`.
4.  Set **Pushurl** to your local server:
    ```
    http://<YOUR_SERVER_IP>:8080/<DEVICE_KEY>
    ```
    *(e.g., http://192.168.1.112:8080/bae3ca6330c547c797f13d231e6040f8)*
5.  **Apply** and click **Test**.

### Why use this version with Unraid?
-   **Structured POST Support**: This Python implementation explicitly handles the complex POST requests Unraid sends, extracting the `title`, `body`, and `importance` correctly.
-   **Local Audit Trail**: Every Unraid system alert is logged into your local `log.log` and `bark.db`.
-   **Privacy**: Notifications transit through your local network before final delivery to Apple, keeping logs off third-party cloud servers.

## Project Structure

-   `python_server/`: Source code.
    -   `main.py`: API Endpoints.
    -   `apns.py`: Apple Push Notification logic.
    -   `database.py`: SQLite models.
    -   `config.py`: Server settings.
-   `setup.py`: Packaging and dependency management.
-   `send_message.py`: CLI script for sending notifications.
