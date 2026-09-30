from fastapi import APIRouter, HTTPException

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)
from backend.config import get_settings
from backend.schemas import (
    DocumentRequest,
    DocumentResponse,
)


router = APIRouter()

settings = get_settings()

generator = GeminiDocumentGenerator(
    settings
)


@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(
    request: DocumentRequest,
):

    try:

        document = generator.generate_document(
            request
        )

        if len(document) > settings.max_document_chars:

            raise HTTPException(
                status_code=413,
                detail="Generated document is too large.",
            )

        return DocumentResponse(
            document=document,
            model=settings.gemini_model,
            demo_mode=generator.client is None,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {exc}",
        ) from exc