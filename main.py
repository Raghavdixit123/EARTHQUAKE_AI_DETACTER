
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

USGS_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/all_day.geojson"
)

earthquake_data = []
last_updated = None
feed_status = "Starting"
clients = set()


def fetch_earthquakes():
    """Fetch recent earthquake events from the public USGS feed."""
    response = requests.get(USGS_URL, timeout=15)
    response.raise_for_status()
    data = response.json()

    events = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])

        events.append({
            "id": feature.get("id"),
            "place": props.get("place") or "Location unavailable",
            "magnitude": props.get("mag"),
            "time": props.get("time"),
            "url": props.get("url"),
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2],
            "alert": props.get("alert"),
            "tsunami": props.get("tsunami", 0),
        })

    events.sort(
        key=lambda item: item["time"] or 0,
        reverse=True
    )
    return events


async def refresh_feed():
    global earthquake_data, last_updated, feed_status

    try:
        # Network request runs outside the async event loop.
        events = await asyncio.to_thread(fetch_earthquakes)
        earthquake_data = events
        last_updated = datetime.now(timezone.utc).isoformat()
        feed_status = "Live"

        message = {
            "type": "earthquakes",
            "events": earthquake_data,
            "updated": last_updated,
            "status": feed_status,
        }

        disconnected = []
        for websocket in list(clients):
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            clients.discard(websocket)

    except Exception as exc:
        feed_status = f"Feed unavailable: {type(exc).__name__}"
        print("USGS feed error:", repr(exc))


async def poll_usgs():
    while True:
        await refresh_feed()
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(poll_usgs())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Earthquake Alert Dashboard", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


@app.get("/api/earthquakes")
async def get_earthquakes():
    return {
        "events": earthquake_data,
        "updated": last_updated,
        "status": feed_status,
        "count": len(earthquake_data),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        await websocket.send_json({
            "type": "earthquakes",
            "events": earthquake_data,
            "updated": last_updated,
            "status": feed_status,
        })

        while True:
            # Keep connection alive while waiting for browser messages.
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print("WebSocket error:", repr(exc))
    finally:
        clients.discard(websocket)
