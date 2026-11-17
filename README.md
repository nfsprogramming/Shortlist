# Shortlist: AI Resume Screening & Job Recommendation Engine

[![CI](https://github.com/nfsprogramming/Shortlist/actions/workflows/ci.yml/badge.svg)](https://github.com/nfsprogramming/Shortlist/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

Shortlist is a lightweight, privacy-focused resume screening and job recommendation web application built with Python (Flask) and scikit-learn. It extracts skills and experience from candidate resumes, screens candidates against specific job descriptions using composite TF-IDF and skill coverage scoring, matches candidates to open roles, and identifies top skill gaps.

All analysis runs locally in memory—resumes and candidate details are never stored or transmitted to third-party APIs.

---

## Features

- **Multi-Format Ingestion**: Supports PDF uploads (via `pypdf`), Markdown (`.md`), plain text (`.txt`), and direct text pasting.
- **Candidate Profile Extraction**:
  - Automatically identifies candidate contact information (email, phone, name heuristic).
  - Calculates years of professional experience using regex-based extraction.
  - Computes document word count and parsed text statistics.
- **Dictionary-Based Skill Matching**:
  - Uses regex boundary assertions (`(?<![\w+#.])` and `(?![\w+#])`) against a comprehensive skills database (`data/skills.json`).
  - Prevents false-positive substring matches (e.g., prevents matching "Java" within "JavaScript" or "C" within "CSS").
- **Composite Screening Scoring**:
  - When screened against a target Job Description, scores candidates using:
    - **65% Required Skill Coverage**: Ratio of identified candidate skills to job requirements.
    - **35% Sublinear TF-IDF Cosine Similarity**: Unigram and bigram text vectorization compared against calibrated baseline similarity.
  - Automated verdict classification:
    - **Shortlist**: Match score $\ge 70\%$
    - **Review**: Match score between $45\%$ and $69\%$
    - **Not a fit**: Match score $< 45\%$
- **Role Recommendations**:
  - Evaluates candidate profiles against an internal job database (`data/jobs.json`).
  - Weighted matching: 55% required skills, 15% nice-to-have skills, and 30% scaled TF-IDF text similarity.
  - Returns top 8 role recommendations with progress meters and itemized skill matches.
- **Skill Gap Detection**:
  - Aggregates and ranks the most frequent missing skills across the top matching roles to highlight candidate upskilling opportunities.
- **Responsive Single-Page Interface**:
  - Drag-and-drop file upload zone with file size validation.
  - Preloaded sample data button for instant testing.
  - Visual scorecard with animated SVG circular gauges, skill chip filters, and missing skill badges.

---

## Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Flask (>=3.0) | Lightweight REST API and static asset hosting |
| **NLP & Matching** | scikit-learn (>=1.3) | TF-IDF vectorization and cosine similarity calculations |
| **PDF Extraction** | pypdf (>=4.0) | In-memory PDF text stream extraction and decrypt handling |
| **Test Fixtures** | reportlab (>=4.0) | Programmatic PDF generation for test assertions |
| **Frontend UI** | HTML5, CSS3, JavaScript | Zero-framework responsive single-page application |
| **Packaging** | setuptools / pyproject.toml | Standard Python packaging specifications |

---

## Prerequisites

- Python 3.10, 3.11, or 3.12
- `pip` package manager
- (Optional) `git` for version control

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nfsprogramming/Shortlist.git
   cd Shortlist
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Windows (Command Prompt)
   python -m venv venv
   .\venv\Scripts\activate.bat
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Configuration

The application requires minimal configuration and works out of the box with sensible defaults:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `5000` | The local port on which the Flask server listens |
| `MAX_CONTENT_LENGTH` | `5242880` (5 MB) | Configured in `app.py` for maximum allowed upload payload |

---

## Usage

### 1. Running the Web Application

Start the local Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 2. REST API Reference

#### Health Check
- **Endpoint:** `GET /api/health`
- **Response:**
  ```json
  {
    "jobs": 8,
    "status": "ok"
  }
  ```

#### List Available Jobs
- **Endpoint:** `GET /api/jobs`
- **Response:** Array of job objects containing `id`, `title`, `company`, `location`, `level`, `description`, `required`, and `nice` skills.

#### Analyze Resume
- **Endpoint:** `POST /api/analyze`
- **Content-Type:** `multipart/form-data` or `application/x-www-form-urlencoded`
- **Parameters:**
  - `resume`: (Optional file upload) PDF, TXT, or MD file (up to 5 MB).
  - `resume_text`: (Optional string) Plain text resume content (minimum 40 characters).
  - `job_description`: (Optional string) Target job description for targeted screening.
- **Example cURL (Form Upload):**
  ```bash
  curl -X POST http://127.0.0.1:5000/api/analyze \
    -F "resume=@sample_resume.pdf" \
    -F "job_description=Machine Learning Engineer with Python and PyTorch experience."
  ```
- **Example cURL (Pasted Text):**
  ```bash
  curl -X POST http://127.0.0.1:5000/api/analyze \
    -d "resume_text=Jane Doe. Python, SQL, Docker, Flask developer with 4 years experience." \
    -d "job_description=Backend Engineer requiring Python and SQL."
  ```

---

## Customization

### Adding or Modifying Roles
Job listings are stored in [`data/jobs.json`](data/jobs.json). Each entry follows this structure:
```json
{
  "id": "ml-eng",
  "title": "Machine Learning Engineer",
  "company": "Prism AI",
  "location": "Bengaluru / Hybrid",
  "level": "Mid",
  "description": "Train and deploy deep learning models...",
  "required": ["python", "machine learning", "deep learning", "pytorch", "pandas", "sql"],
  "nice": ["docker", "aws", "git"]
}
```

### Extending Skills Dictionary
Skill keywords and their case-insensitive synonyms are maintained in [`data/skills.json`](data/skills.json):
```json
{
  "python": ["python", "python3", "py"],
  "pytorch": ["pytorch", "torch"],
  "scikit-learn": ["scikit-learn", "sklearn"]
}
```

---

## Project Structure

```
Shortlist/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Automated CI test matrix (Python 3.10, 3.11, 3.12)
│       └── release.yml          # Tag-triggered release packaging & asset publisher
├── data/
│   ├── jobs.json                # Job postings catalog with skill requirements
│   └── skills.json              # Canonical skills list and alias mappings
├── engine/
│   ├── __init__.py              # Public exports for matching and parsing engines
│   ├── matcher.py               # TF-IDF similarity, scoring weights, verdicts, and recommendations
│   ├── parser.py                # PDF extraction via pypdf, text sanitization, validation
│   └── skills.py                # Regex extraction for skills, contact data, and experience
├── static/
│   ├── app.js                   # Client logic, file drag-and-drop, API requests, dynamic DOM rendering
│   ├── index.html               # Semantic HTML5 single-page application structure
│   └── style.css                # Responsive layout, animations, color system, and typography
├── tests/
│   └── test_app.py              # Automated test suite (health, parsing, scoring, error handling)
├── .gitignore                   # Stack-tailored git exclusion rules
├── app.py                       # Flask server entry point and API route definitions
├── LICENSE                      # MIT License
├── pyproject.toml               # Python project configuration and package metadata
├── README.md                    # Project documentation
├── requirements.txt             # Core and development dependencies
├── uv.lock                      # Universal dependency lockfile
└── vercel.json                  # Vercel serverless deployment and routing rules
```

---

## Testing

Run the test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

The automated test suite verifies:
- API health check response and job catalog integration.
- Root route static HTML delivery.
- In-memory PDF synthesis (via ReportLab) and text extraction.
- Edge cases: bad file extensions, non-PDF payloads, empty submissions, and character length limits.
- Precise regex boundary isolation (e.g. verifying that "Java" does not match within "JavaScript").

---

## Release & Downloads

Standalone application archives are published on GitHub Releases:
- Download the latest packaged release: [GitHub Releases](https://github.com/nfsprogramming/Shortlist/releases)
- Every release artifact includes SHA-256 checksums (`checksums.txt`) for integrity verification.

---

## Limitations

- **Scanned Resumes**: Resumes formatted purely as raster images inside PDFs contain no text stream and require OCR preprocessing or direct text pasting.
- **Page & Size Limits**: Hardcoded limits in `engine/parser.py` restrict analysis to a maximum of 15 pages per PDF and a 5 MB upload payload to ensure low latency.
- **Keyword Boundary Rules**: Skills with non-standard punctuation outside defined alias dictionaries should be added to `data/skills.json` to ensure detection.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-new-feature`.
3. Commit your changes: `git commit -m "Add feature"`.
4. Ensure all tests pass: `python -m unittest discover -s tests -v`.
5. Push to your branch: `git push origin feature/my-new-feature`.
6. Open a Pull Request.

---

## License

This project is open source and available under the [MIT License](LICENSE).
