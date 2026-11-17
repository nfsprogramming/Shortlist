const $ = (id) => document.getElementById(id);
const SAMPLE = `Asha Kumar
asha@example.com
AI & Data Science student with 2 years of project experience.
Skills: Python, Pandas, NumPy, scikit-learn, TensorFlow, SQL, Flask REST APIs, React, JavaScript, Git, Docker.
Projects: NLP legal assistant using transformers; solar flare machine learning pipeline; full stack apps with Node.js and MongoDB.
Strong communication and teamwork.`;
const SAMPLE_JD = "Machine Learning Engineer. Requirements: Python, machine learning, deep learning, PyTorch, pandas, SQL and AWS. Git and Docker are a plus.";

let mode = "file";
let picked = null;

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const chips = (list, cls = "") => list.length ? `<div class="chips">${list.map((s) => `<span class="chip ${cls}">${esc(s)}</span>`).join("")}</div>` : `<small>None</small>`;

function showError(msg) { const e = $("err"); e.textContent = msg; e.hidden = !msg; }

function setMode(m) {
  mode = m;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t.dataset.tab === m));
  $("drop").hidden = m !== "file";
  $("text").hidden = m !== "text";
  showError("");
}

function setFile(f) {
  if (!f) return;
  if (f.size > 5 * 1024 * 1024) { showError("File is too large. The limit is 5 MB."); return; }
  picked = f;
  $("drop").classList.add("has");
  $("dropTitle").textContent = f.name;
  $("dropSub").textContent = `${(f.size / 1024).toFixed(0)} KB. Click to choose a different file`;
  showError("");
}

document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => setMode(t.dataset.tab)));
$("file").addEventListener("change", (e) => setFile(e.target.files[0]));
$("drop").addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("file").click(); } });
["dragover", "dragenter"].forEach((ev) => $("drop").addEventListener(ev, (e) => { e.preventDefault(); $("drop").classList.add("over"); }));
["dragleave", "drop"].forEach((ev) => $("drop").addEventListener(ev, (e) => { e.preventDefault(); $("drop").classList.remove("over"); }));
$("drop").addEventListener("drop", (e) => setFile(e.dataTransfer.files[0]));
$("sample").addEventListener("click", () => { setMode("text"); $("text").value = SAMPLE; $("jd").value = SAMPLE_JD; });

$("go").addEventListener("click", async () => {
  const body = new FormData();
  if (mode === "file") {
    if (!picked) return showError("Choose a resume file first, or switch to Paste text.");
    body.append("resume", picked);
  } else {
    if (!$("text").value.trim()) return showError("Paste your resume text first.");
    body.append("resume_text", $("text").value);
  }
  body.append("job_description", $("jd").value);
  const btn = $("go");
  btn.disabled = true; btn.textContent = "Analyzing…"; showError("");
  try {
    const res = await fetch("/api/analyze", { method: "POST", body });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Something went wrong. Try again.");
    render(data);
  } catch (err) {
    showError(err.message || "Could not reach the server. Is it running?");
  } finally {
    btn.disabled = false; btn.textContent = "Analyze resume";
  }
});

function render(d) {
  const p = d.profile, s = d.screening;
  const color = (n) => (n >= 70 ? "#3fae2a" : n >= 45 ? "#3a1fff" : "#ff5c7a");
  let h = `<div class="block"><h2>${esc(p.name || "Your profile")}</h2>
    <p class="who">${p.email ? `<span>${esc(p.email)}</span>` : ""}${p.phone ? `<span>${esc(p.phone)}</span>` : ""}
    <span><b>${p.skills.length}</b> skills found</span><span><b>${p.years || "No"}</b> years mentioned</span></p>${chips(p.skills)}</div>`;
  if (s) {
    h += `<div class="block"><h2>Screening result</h2><div class="screen">
      <div class="ring" data-p="${s.score}" style="--c:${color(s.score)}"><div>${s.score}%</div></div>
      <div><p class="verdict">${esc(s.verdict)}</p>
      <small>${s.matched.length} of ${s.required_count} required skills matched. Text similarity ${s.text_similarity}%.</small>
      ${s.note ? `<p><small>${esc(s.note)}</small></p>` : ""}</div></div>
      <p class="label">Matched</p>${chips(s.matched, "ok")}<p class="label">Missing</p>${chips(s.missing, "no")}</div>`;
  }
  h += `<div class="block"><h2>Recommended jobs</h2>` + d.recommendations.map((j) => `
    <div class="job-card"><div class="jr"><h3>${esc(j.title)}</h3><span class="s">${j.score}%</span></div>
    <p class="meta">${esc(j.company)}, ${esc(j.location)}. ${esc(j.level)} level</p>
    <div class="bar"><i data-w="${j.score}" style="width:0"></i></div>
    ${chips(j.matched, "ok")}${j.missing.length ? `<div style="height:6px"></div>${chips(j.missing, "no")}` : ""}</div>`).join("") + `</div>`;
  if (d.skill_gaps.length) h += `<div class="block"><h2>Skills to learn next</h2><small>Missing most often from your top matches</small><div style="height:8px"></div>${chips(d.skill_gaps, "no")}</div>`;

  const out = $("results");
  out.innerHTML = h; out.hidden = false;
  requestAnimationFrame(() => {
    out.querySelectorAll(".ring").forEach((r) => r.style.setProperty("--p", r.dataset.p));
    out.querySelectorAll(".bar i").forEach((b) => (b.style.width = b.dataset.w + "%"));
  });
  out.scrollIntoView({ behavior: "smooth", block: "start" });
}
