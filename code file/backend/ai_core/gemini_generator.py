import time

from google import genai
from google.genai import types

from backend.config import Settings
from backend.schemas import DocumentRequest
from backend.utils.sanitize import sanitize_text, split_terms


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI-assisted legal document drafting assistant.

Create professional legal document drafts from facts supplied by the user.

Rules:

1. Do not invent names.
2. Do not invent dates.
3. Do not invent addresses.
4. Do not invent monetary values.
5. Do not invent governing laws.
6. Do not invent legal citations.
7. Do not invent obligations that the user did not request.
8. If information is missing, use [TO BE COMPLETED].
9. Preserve the user's supplied terms.
10. Use professional and readable legal language.
11. Use numbered clauses and clear headings.
12. Include signature blocks.
13. This is drafting assistance, not legal advice.
14. Return only the document.
""".strip()


class GeminiDocumentGenerator:

    def __init__(self, settings: Settings):

        self.settings = settings
        self.client = None

        if settings.gemini_api_key:
            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    def generate_document(
        self,
        request: DocumentRequest,
    ) -> str:

                # Demo mode takes priority when enabled.
        # This makes automated tests deterministic and
        # avoids calling the Gemini API during demo mode.
        if self.settings.demo_mode:
            return self._demo_document(request)

        # Production mode requires a Gemini API client.
        if self.client is None:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        prompt = self._build_prompt(request)

        # Try the configured model first.
        models_to_try = [
            self.settings.gemini_model,
            "gemini-3.7-flash",
            "gemini-3.6-flash",
        ]

        last_error = None

        for model in models_to_try:

            # Don't retry the same model twice.
            if (
                model
                != self.settings.gemini_model
                and model
                in models_to_try[
                    :models_to_try.index(model)
                ]
            ):
                continue

            for attempt in range(3):

                try:

                    response = (
                        self.client.models.generate_content(

                            model=model,

                            contents=prompt,

                            config=types.GenerateContentConfig(

                                system_instruction=(
                                    SYSTEM_INSTRUCTION
                                ),

                                temperature=0.35,

                                max_output_tokens=6000,
                            ),
                        )
                    )

                    generated_text = getattr(
                        response,
                        "text",
                        None,
                    )

                    if not generated_text:
                        raise RuntimeError(
                            "Gemini returned an empty response."
                        )

                    return sanitize_text(
                        generated_text
                    )

                except Exception as exc:

                    last_error = exc

                    error_text = str(exc)

                    # Retry temporary 503 / unavailable errors.
                    temporary_error = (
                        "503" in error_text
                        or "UNAVAILABLE" in error_text
                        or "high demand" in error_text.lower()
                        or "temporarily" in error_text.lower()
                    )

                    if not temporary_error:
                        raise

                    # Exponential backoff:
                    # 2 sec -> 4 sec -> 8 sec
                    wait_seconds = 2 ** (
                        attempt + 1
                    )

                    time.sleep(
                        wait_seconds
                    )

        raise RuntimeError(
            "Gemini is temporarily unavailable. "
            "The configured Gemini models were "
            "unable to process the request after "
            "multiple attempts. "
            f"Last error: {last_error}"
        )

    def _build_prompt(
        self,
        request: DocumentRequest,
    ) -> str:

        terms = split_terms(
            request.terms
        )

        formatted_terms = "\n".join(
            f"- {term}"
            for term in terms
        )

        return f"""
Create a professional legal document draft.

DOCUMENT TYPE:
{request.document_type}

PARTIES:
{request.parties}

EFFECTIVE DATE:
{request.effective_date}

USER-PROVIDED TERMS:
{formatted_terms}

Requirements:

1. Begin with the document title.
2. Identify the parties.
3. State the effective date.
4. Create clear sections.
5. Use numbered clauses.
6. Preserve every user-provided term.
7. Do not fabricate missing facts.
8. Use [TO BE COMPLETED] when necessary.
9. Include signature blocks.
10. Keep the document editable.
11. Do not use Markdown code fences.
12. Return only the legal document.
""".strip()

    def _demo_document(
        self,
        request: DocumentRequest,
    ) -> str:

        terms = split_terms(
            request.terms
        )

        if terms:

            term_lines = "\n".join(
                f"{index}. {term}"
                for index, term in enumerate(
                    terms,
                    start=1,
                )
            )

        else:

            term_lines = "[TO BE COMPLETED]"

        return f"""
{request.document_type.upper()} (NDA)

EFFECTIVE DATE

{request.effective_date}

PARTIES

{request.parties}

1. PURPOSE AND SCOPE

This document is an AI-assisted draft prepared
from the information supplied by the user.

The parties should review all information and
complete any missing details before signing.

2. AGREED TERMS

{term_lines}

3. GENERAL PROVISIONS

The parties intend to perform their respective
obligations according to the completed terms of
this document.

4. CONFIDENTIALITY

Where confidentiality obligations are applicable,
the parties should specify the information that
must be protected.

5. TERMINATION

The parties should review and specify applicable
termination rights and notice periods.

6. GOVERNING LAW

[TO BE COMPLETED]

7. SIGNATURES

PARTY 1

Signature: ______________________________

Name: __________________________________

Date: ___________________________________

PARTY 2

Signature: ______________________________

Name: __________________________________

Date: ___________________________________
""".strip()