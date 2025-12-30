import uuid
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from .database import engine, init_db, get_db, Device, MessageLog
import time
from .apns import apns_client
from .logger import logger

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bark Server starting up...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    yield
    logger.info("Bark Server shutting down...")

app = FastAPI(title="Bark Server Python", lifespan=lifespan)

# Verbose Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.4f}s")
    return response

@app.get("/ping")
def ping():
    return {"code": 200, "message": "pong", "timestamp": int(1)}

# --- Register ---

@app.post("/register")
@app.get("/register") # Support GET for compatibility
async def register(
    device_token: str = None, 
    key: str = None, 
    devicetoken: str = None, # Old support
    db: Session = Depends(get_db)
):
    token = device_token or devicetoken
    if not token:
        raise HTTPException(status_code=400, detail="device token is empty")
    
    # Generate Key if not provided
    if not key:
        key = str(uuid.uuid4()).replace("-", "")
    
    # Check if key exists
    existing_device = db.query(Device).filter(Device.device_key == key).first()
    
    if existing_device:
        existing_device.device_token = token
    else:
        new_device = Device(device_key=key, device_token=token)
        db.add(new_device)
    
    db.commit()
    
    return {
        "code": 200, 
        "message": "success", 
        "data": {
            "key": key,
            "device_key": key,
            "device_token": token
        }
    }

# --- Push Logic ---

async def do_push(key: str, title: str, body: str, subtitle: str = None, params: Dict[str, Any] = None, db: Session = None):
    # Lookup Device
    device = db.query(Device).filter(Device.device_key == key).first()
    if not device:
        logger.warning(f"Push attempt for unknown device_key={key}")
        return {"code": 404, "message": "Device not found"}
    
    # Construct Payload
    payload = {
        "aps": {
            "alert": {
                "title": title,
                "body": body,
            },
            "sound": "1107"
        }
    }
    
    if subtitle:
         payload["aps"]["alert"]["subtitle"] = subtitle

    # Process Extra Params (isArchive, automaticallyCopy, etc.)
    if params:
        for k, v in params.items():
             payload[k] = v
        
        # Handle special Bark params that map to APS
        if "sound" in params:
             payload["aps"]["sound"] = params["sound"]

    # Send
    success, reason = await apns_client.push(device.device_token, payload)
    
    if success:
        logger.info(f"Push SUCCESS | Key: {key} | Title: {title} | Body: {body}")
        log_entry = MessageLog(
            timestamp=int(time.time()),
            device_key=key,
            title=title,
            body=body,
            status="success",
        )
        db.add(log_entry)
        db.commit()
        return {"code": 200, "message": "success"}
    elif reason == "Unregistered":
        logger.warning(f"Push UNREGISTERED | Key: {key} | Title: {title} | Body: {body}")
        log_entry = MessageLog(
            timestamp=int(time.time()),
            device_key=key,
            title=title,
            body=body,
            status="unregistered",
        )
        db.add(log_entry)
        # Remove invalid device
        db.delete(device)
        db.commit()
        return {"code": 410, "message": "Device unregistered"}
    else:
        logger.error(f"Push FAILED | Key: {key} | Title: {title} | Body: {body} | Reason: {reason}")
        log_entry = MessageLog(
            timestamp=int(time.time()),
            device_key=key,
            title=title,
            body=body,
            status=f"failed: {reason}",
        )
        db.add(log_entry)
        db.commit()
        return {"code": 500, "message": f"Push failed: {reason}"}


# --- Push Endpoints ---

@app.post("/{key}")
async def push_structured(key: str, request: Request, db: Session = Depends(get_db)):
    """Handles POST requests where title/body are in the JSON or Form body."""
    title = "Bark"
    body = ""
    params = {}

    # Try JSON
    try:
        data = await request.json()
        params.update(data)
    except:
        # Try Form
        try:
            form = await request.form()
            params.update(dict(form))
        except:
            pass

    # Extract Title/Body from params
    title = params.get("title", params.get("topic", title))
    body = params.get("body", params.get("text", params.get("message", "")))
    
    # Merge query params
    params.update(dict(request.query_params))
    
    if not body:
        # Compatibility: check if body was passed as a query param instead
        body = params.get("body", "")

    return await do_push(key, title, body, params=params, db=db)

@app.api_route("/{key}/{body}", methods=["GET", "POST"])
async def push_simple(key: str, body: str, request: Request, db: Session = Depends(get_db)):
    params = dict(request.query_params)
    return await do_push(key, "Bark", body, params=params, db=db)

@app.api_route("/{key}/{title}/{body}", methods=["GET", "POST"])
async def push_title(key: str, title: str, body: str, request: Request, db: Session = Depends(get_db)):
    params = dict(request.query_params)
    return await do_push(key, title, body, params=params, db=db)

@app.api_route("/{key}/{title}/{subtitle}/{body}", methods=["GET", "POST"])
async def push_full(key: str, title: str, subtitle: str, body: str, request: Request, db: Session = Depends(get_db)):
    params = dict(request.query_params)
    return await do_push(key, title, body, subtitle=subtitle, params=params, db=db)

# Run direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
