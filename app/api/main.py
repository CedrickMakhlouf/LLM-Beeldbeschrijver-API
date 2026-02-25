import logging

from fastapi import Depends, FastAPI, HTTPException

from app.api.deps import get_generator
from app.models.schemas import DescribeRequest, DescribeResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Beeldbeschrijver API", version="1.0.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "LLM Beeldbeschrijver API"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/describe", response_model=DescribeResponse)
def describe(
    request: DescribeRequest,
    generator=Depends(get_generator),
) -> DescribeResponse:
    """Stuur een screenshot (base64) op en ontvang een toegankelijke schermbeschrijving in het Nederlands."""
    try:
        result = generator.generate(
            image_base64=request.image_base64,
            image_url=request.image_url,
            image_id=request.image_id,
        )
        return DescribeResponse(
            image_id=result["image_id"],
            description=result["description"],
            processing_ms=result["processing_ms"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Describe endpoint fout: %s", exc)
        raise HTTPException(status_code=500, detail="Beschrijving mislukt") from exc
