"""Turns an uploaded file (PDF / TXT / MD) or pasted text into clean plain text."""
import io
import re

from pypdf import PdfReader

MAX_PAGES = 15
MIN_CHARS = 40


class ResumeError(ValueError):
    """A problem with the resume that the user can fix (shown in the UI)."""


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _from_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise ResumeError("This PDF is password protected. Remove the password and upload it again.")
        pages = [(page.extract_text() or "") for page in reader.pages[:MAX_PAGES]]
    except ResumeError:
        raise
    except Exception:
        raise ResumeError("This file could not be read as a PDF. Export it again or paste the text instead.")
    return "\n".join(pages)


def extract_text(filename: str, data: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf") or data[:5] == b"%PDF-":
        text = _from_pdf(data)
    elif name.endswith((".txt", ".md")):
        text = data.decode("utf-8", errors="ignore")
    else:
        raise ResumeError("Unsupported file type. Upload a PDF, TXT or MD file, or paste the text.")
    text = clean_text(text)
    if len(text) < MIN_CHARS:
        raise ResumeError(
            "No readable text was found. If this is a scanned PDF, export a text-based PDF or paste the text instead."
        )
    return text
