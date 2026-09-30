import sys
from pathlib import Path

# ---------------------------------------------------------
# FIX: Allow Streamlit to find the backend package
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------
import requests
import streamlit as st

from backend.services.document_service import (
    format_txt,
    format_docx,
    format_pdf,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
API_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="LegalEase AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .legal-notice {
        padding: 15px;
        border-radius: 8px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">⚖️ LegalEase AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-powered legal document generation assistant</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:

    st.header("⚖️ LegalEase AI")

    st.markdown(
        """
        ### About

        LegalEase AI helps generate draft legal documents
        using Generative AI.

        You can create documents such as:

        - Employment Agreements
        - Non-Disclosure Agreements
        - Lease Agreements
        - Service Agreements
        - Partnership Agreements
        - Other legal drafts
        """
    )

    st.divider()

    st.markdown(
        """
        **Important**

        LegalEase AI generates drafts for educational
        and productivity purposes.

        It is not a substitute for professional legal advice.
        """
    )


# ---------------------------------------------------------
# Document input section
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">📄 Create Your Legal Document</div>',
    unsafe_allow_html=True,
)

document_type = st.selectbox(
    "Document Type",
    [
        "Employment Agreement",
        "Non-Disclosure Agreement",
        "Lease Agreement",
        "Service Agreement",
        "Partnership Agreement",
        "Freelance Agreement",
        "Sales Agreement",
        "Consulting Agreement",
        "Other",
    ],
)

if document_type == "Other":
    custom_document_type = st.text_input(
        "Enter document type",
        placeholder="Example: Software Licensing Agreement",
    )

    if custom_document_type.strip():
        document_type = custom_document_type


parties = st.text_area(
    "Parties",
    placeholder=(
        "Example:\n"
        "Alice Smith (Employee)\n"
        "ABC Technologies Pvt. Ltd. (Employer)"
    ),
    height=120,
)


effective_date = st.text_input(
    "Effective Date",
    placeholder="Example: September 29, 2026",
)


terms = st.text_area(
    "Terms and Conditions",
    placeholder=(
        "Example:\n"
        "- Confidential information must be protected\n"
        "- Agreement lasts for two years\n"
        "- Either party may terminate with 30 days notice\n"
        "- Payment terms are monthly"
    ),
    height=220,
)


# ---------------------------------------------------------
# Generate button
# ---------------------------------------------------------
generate_button = st.button(
    "✨ Generate Legal Document",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# Generate document
# ---------------------------------------------------------
if generate_button:

    if not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        }

        with st.spinner("🤖 Generating your legal document..."):

            try:

                response = requests.post(
                    f"{API_URL}/generate",
                    json=payload,
                    timeout=180,
                )

                if response.status_code == 200:

                    result = response.json()

                    # Try common response field names
                    generated_document = (
                        result.get("document")
                        or result.get("content")
                        or result.get("text")
                        or result.get("generated_text")
                        or result.get("document_text")
                    )

                    if not generated_document:
                        st.error(
                            "The API responded successfully, "
                            "but no generated document was returned."
                        )

                        st.json(result)

                    else:

                        st.session_state["generated_document"] = (
                            generated_document
                        )

                        st.session_state["document_type"] = (
                            document_type
                        )

                        st.session_state["parties"] = parties

                        st.session_state["effective_date"] = (
                            effective_date
                        )

                        st.session_state["terms"] = terms

                        st.success(
                            "✅ Legal document generated successfully!"
                        )

                else:

                    st.error(
                        f"Backend returned HTTP {response.status_code}"
                    )

                    try:
                        st.json(response.json())
                    except Exception:
                        st.code(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to the LegalEase backend."
                )

                st.info(
                    "Make sure FastAPI is running on "
                    "http://127.0.0.1:8000"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ The request timed out. "
                    "Please try again."
                )

            except Exception as e:

                st.error(
                    f"An unexpected error occurred: {e}"
                )


# ---------------------------------------------------------
# Generated document editor
# ---------------------------------------------------------
if "generated_document" in st.session_state:

    st.divider()

    st.markdown(
        '<div class="section-title">📝 Edit Your Document</div>',
        unsafe_allow_html=True,
    )

    edited_document = st.text_area(
        "Generated Legal Document",
        value=st.session_state["generated_document"],
        height=600,
    )

    # Save edits into session state
    st.session_state["generated_document"] = edited_document


    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">👁️ Document Preview</div>',
        unsafe_allow_html=True,
    )

    preview_text = edited_document.replace(
        "\n",
        "<br>",
    )

    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd;
            padding: 30px;
            border-radius: 10px;
            background: white;
            color: black;
            min-height: 300px;
        ">
            {preview_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # Download section
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">⬇️ Download Document</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------
    with col1:

        try:

            txt_data = format_txt(
                edited_document
            )

        except TypeError:

            txt_data = edited_document

        st.download_button(
            label="📄 Download TXT",
            data=txt_data,
            file_name="LegalEase_Document.txt",
            mime="text/plain",
            use_container_width=True,
        )


    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------
    with col2:

        try:

            docx_data = format_docx(
                edited_document
            )

            st.download_button(
                label="📝 Download DOCX",
                data=docx_data,
                file_name="LegalEase_Document.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as e:

            st.error(
                f"DOCX generation error: {e}"
            )


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------
    with col3:

        try:

            pdf_data = format_pdf(
                edited_document
            )

            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name="LegalEase_Document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as e:

            st.error(
                f"PDF generation error: {e}"
            )


# ---------------------------------------------------------
# Legal disclaimer
# ---------------------------------------------------------
st.markdown(
    """
    <div class="legal-notice">
        ⚠️ <strong>Legal Disclaimer:</strong>
        LegalEase AI generates draft legal documents for
        educational and productivity purposes. The generated
        content should be reviewed by a qualified legal
        professional before being used as a legally binding
        document.
    </div>
    """,
    unsafe_allow_html=True,
)