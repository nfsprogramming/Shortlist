"""TF-IDF similarity + skill coverage scoring for screening and job recommendation."""
import json
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from .skills import DATA, extract_contact, extract_skills, extract_years

SIM_FULL = 0.30  # cosine similarity treated as a "perfect" text match


@lru_cache(maxsize=1)
def load_jobs() -> list[dict]:
    return json.loads((DATA / "jobs.json").read_text(encoding="utf-8"))


def _coverage(have: set, need: list):
    matched = [s for s in need if s in have]
    missing = [s for s in need if s not in have]
    return matched, missing, (len(matched) / len(need) if need else 0.0)


def _job_text(job: dict) -> str:
    return " ".join([job["title"], job["description"], *job["required"], *job["nice"]])


def _similarities(resume: str, docs: list) -> list:
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    matrix = vec.fit_transform([resume, *docs])
    return linear_kernel(matrix[0:1], matrix[1:]).ravel().tolist()


def _scale(sim: float) -> float:
    return min(1.0, sim / SIM_FULL)


def _verdict(score: int) -> str:
    return "Shortlist" if score >= 70 else "Review" if score >= 45 else "Not a fit"


def analyze(resume: str, job_description: str = "") -> dict:
    have = set(extract_skills(resume))
    jobs = load_jobs()
    jd = (job_description or "").strip()
    sims = _similarities(resume, [_job_text(j) for j in jobs] + ([jd] if jd else []))

    recs = []
    for job, sim in zip(jobs, sims):
        req_m, req_x, req_r = _coverage(have, job["required"])
        nice_m, _, nice_r = _coverage(have, job["nice"])
        score = round(100 * (0.55 * req_r + 0.15 * nice_r + 0.30 * _scale(sim)))
        recs.append({**job, "score": score, "matched": req_m, "missing": req_x, "nice_matched": nice_m})
    recs.sort(key=lambda r: r["score"], reverse=True)

    gaps: dict = {}
    for r in recs[:3]:
        for s in r["missing"]:
            gaps[s] = gaps.get(s, 0) + 1
    skill_gaps = [s for s, _ in sorted(gaps.items(), key=lambda kv: (-kv[1], kv[0]))][:6]

    screening = None
    if jd:
        need = extract_skills(jd)
        matched, missing, ratio = _coverage(have, need)
        sim = _scale(sims[-1])
        score = round(100 * (0.65 * ratio + 0.35 * sim)) if need else round(100 * sim)
        screening = {
            "score": score,
            "verdict": _verdict(score),
            "matched": matched,
            "missing": missing,
            "required_count": len(need),
            "text_similarity": round(sims[-1] * 100),
            "note": "" if need else "No known skills were found in the job description, so only text similarity was used.",
        }

    return {
        "profile": {**extract_contact(resume), "skills": sorted(have), "years": extract_years(resume),
                    "word_count": len(resume.split())},
        "screening": screening,
        "recommendations": recs[:8],
        "skill_gaps": skill_gaps,
    }
