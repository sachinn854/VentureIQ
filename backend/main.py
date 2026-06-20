import asyncio
import uuid
import logging
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi.errors import RateLimitExceeded

from backend.config import settings
from backend.schemas.models import IdeaRequest, AnalyzeResponse, FinalReport
from backend.security.input_sanitizer import sanitize
from backend.security.rate_limiter import limiter
from backend.graph.startup_graph import run_graph
from backend.pdf_generator import generate_pdf

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

app = FastAPI(title='Startup Validator API')

# ─── CORS ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)

# ─── Rate Limiter ─────────────────────────────────────────────────────────────

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={'detail': 'Too many requests. Please wait and try again.'})

# ─── In-memory stores ─────────────────────────────────────────────────────────

_queues:  dict[str, asyncio.Queue]           = {}
_reports: dict[str, tuple[FinalReport, str]] = {}


async def _run_and_capture(run_id: str, idea: str, queue: asyncio.Queue):
    raw_queue: asyncio.Queue = asyncio.Queue()

    async def _graph_task():
        await run_graph(idea, raw_queue)

    asyncio.create_task(_graph_task())

    while True:
        event = await raw_queue.get()

        if event.get('type') == 'final_report' and event.get('data'):
            try:
                _reports[run_id] = (FinalReport(**event['data']), idea)
                logger.info(f"[{run_id[:8]}] Final report stored — verdict: {event['data'].get('verdict')} score: {event['data'].get('overall_score')}")
                # Purge old reports to prevent memory leak (keep last 50)
                if len(_reports) > 50:
                    oldest = next(iter(_reports))
                    _reports.pop(oldest)
            except Exception as e:
                logger.error(f"[{run_id[:8]}] Failed to store report: {e}")

        if event.get('type') == 'error':
            logger.error(f"[{run_id[:8]}] Agent error [{event.get('agent')}]: {event.get('message')}")

        if event.get('type') in ('agent_start', 'agent_complete'):
            logger.info(f"[{run_id[:8]}] {event['type'].upper()} → {event.get('agent')}")

        await queue.put(event)

        if event.get('type') == 'done':
            break


# ─── POST /api/analyze ────────────────────────────────────────────────────────

@app.post('/api/analyze', response_model=AnalyzeResponse)
@limiter.limit('5/minute;50/day')
async def analyze(request: Request, body: IdeaRequest):
    clean_idea = sanitize(body.idea)
    run_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    _queues[run_id] = queue

    logger.info(f"[{run_id[:8]}] New analysis started — idea length: {len(clean_idea)} chars")
    asyncio.create_task(_run_and_capture(run_id, clean_idea, queue))

    return AnalyzeResponse(run_id=run_id)


# ─── WS /ws/{run_id} ─────────────────────────────────────────────────────────

@app.websocket('/ws/{run_id}')
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    try:
        UUID(run_id)
    except ValueError:
        await websocket.close(code=4003, reason='Invalid run_id.')
        return

    if run_id not in _queues:
        await websocket.close(code=4004, reason='Run not found.')
        return

    await websocket.accept()
    queue = _queues[run_id]
    logger.info(f"[{run_id[:8]}] WebSocket connected")

    try:
        while True:
            event: dict = await asyncio.wait_for(queue.get(), timeout=180.0)
            await websocket.send_json(event)
            if event.get('type') == 'done':
                logger.info(f"[{run_id[:8]}] Run complete — WebSocket closing")
                break

    except asyncio.TimeoutError:
        logger.warning(f"[{run_id[:8]}] WebSocket timed out")
        await websocket.send_json({'type': 'error', 'message': 'Analysis timed out.'})

    except WebSocketDisconnect:
        logger.info(f"[{run_id[:8]}] WebSocket disconnected by client")

    finally:
        _queues.pop(run_id, None)
        try:
            await websocket.close()
        except Exception:
            pass


# ─── GET /api/report/{run_id}/pdf ────────────────────────────────────────────

@app.get('/api/report/{run_id}/pdf')
async def download_pdf(run_id: str):
    if run_id not in _reports:
        return JSONResponse(status_code=404, content={'detail': 'Report not ready yet.'})

    report, idea = _reports[run_id]
    pdf_bytes = generate_pdf(report, idea)
    logger.info(f"[{run_id[:8]}] PDF downloaded")

    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="startup-report-{run_id[:8]}.pdf"'},
    )


# ─── GET /health ──────────────────────────────────────────────────────────────

@app.get('/health')
async def health():
    return {'status': 'ok', 'model': settings.model_name}
