import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import app  # noqa: E402

RESUME = """Asha Kumar
asha@example.com +91 98765 43210
AI & Data Science student with 2 years of project experience.
Skills: Python, Pandas, NumPy, scikit-learn, TensorFlow, SQL, Flask REST APIs, React, JavaScript, Git, Docker.
Built an NLP legal assistant using transformers and a solar flare machine learning pipeline."""
JD = "Machine Learning Engineer. Requirements: Python, machine learning, deep learning, PyTorch, pandas, SQL, AWS."


def make_pdf(text: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    for line in text.splitlines():
        c.drawString(40, y, line[:95])
        y -= 18
    c.save()
    return buf.getvalue()


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def test_health(self):
        self.assertEqual(self.c.get("/api/health").get_json()["status"], "ok")

    def test_index_served(self):
        self.assertEqual(self.c.get("/").status_code, 200)

    def test_text_analysis_with_jd(self):
        r = self.c.post("/api/analyze", data={"resume_text": RESUME, "job_description": JD})
        d = r.get_json()
        self.assertEqual(r.status_code, 200)
        self.assertIn("python", d["profile"]["skills"])
        self.assertNotIn("java", d["profile"]["skills"])  # must not match inside "javascript"
        self.assertEqual(d["profile"]["email"], "asha@example.com")
        self.assertEqual(d["profile"]["years"], 2)
        self.assertIn("pytorch", d["screening"]["missing"])
        self.assertEqual(len(d["recommendations"]), 8)
        self.assertTrue(all(0 <= x["score"] <= 100 for x in d["recommendations"]))

    def test_pdf_upload(self):
        data = {"resume": (io.BytesIO(make_pdf(RESUME)), "resume.pdf")}
        r = self.c.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        self.assertIn("machine learning", r.get_json()["profile"]["skills"])

    def test_bad_inputs(self):
        self.assertEqual(self.c.post("/api/analyze", data={}).status_code, 400)
        bad = {"resume": (io.BytesIO(b"not a pdf at all"), "x.pdf")}
        self.assertEqual(self.c.post("/api/analyze", data=bad, content_type="multipart/form-data").status_code, 400)
        exe = {"resume": (io.BytesIO(b"abc"), "x.exe")}
        self.assertEqual(self.c.post("/api/analyze", data=exe, content_type="multipart/form-data").status_code, 400)


if __name__ == "__main__":
    unittest.main()
