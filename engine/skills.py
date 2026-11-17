"""Dictionary based skill, contact and experience extraction."""
import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=1)
def _patterns():
    skills = json.loads((DATA / "skills.json").read_text(encoding="utf-8"))
    compiled = {}
    for canonical, aliases in skills.items():
        alts = "|".join(re.escape(a) for a in sorted(set(aliases + [canonical]), key=len, reverse=True))
        compiled[canonical] = re.compile(r"(?<![\w+#.])(?:" + alts + r")(?![\w+#])", re.IGNORECASE)
    return compiled


def extract_skills(text: str) -> list[str]:
    return [name for name, pat in _patterns().items() if pat.search(text)]


def extract_years(text: str) -> int:
    found = [int(m) for m in re.findall(r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b", text, re.IGNORECASE)]
    return min(max(found), 40) if found else 0


def extract_contact(text: str) -> dict:
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"\+?\d[\d\s().-]{8,16}\d", text)
    name = ""
    for line in text.splitlines()[:5]:
        line = line.strip()
        if line and "@" not in line and not re.search(r"\d", line) and 1 <= len(line.split()) <= 4:
            name = line
            break
    return {"name": name, "email": email.group(0) if email else "", "phone": phone.group(0).strip() if phone else ""}
