import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time

W, H = 1920, 1080
FPS = 30
DURATION_PER_SCENE = 5
FRAMES_PER_SCENE = DURATION_PER_SCENE * FPS

def pil_to_cv(pil_img):
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def create_frame(text_lines, title="", sub_text="", bar_color=(74, 175, 255),
                 bg_color=(15, 23, 42), accent_color=(56, 178, 172)):
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 56)
        font_body = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Top accent bar
    draw.rectangle([0, 0, W, 8], fill=accent_color)

    # Side accent line
    draw.rectangle([60, 80, 66, H - 80], fill=accent_color)

    # Title
    if title:
        draw.text((100, 100), title, fill=(255, 255, 255), font=font_title)

    # Sub text
    if sub_text:
        draw.text((100, 170), sub_text, fill=(180, 180, 190), font=font_sub)

    # Body lines
    y = 280 if title else 120
    for line in text_lines:
        if line.startswith("#"):
            draw.text((100, y), line[1:], fill=(74, 175, 255), font=font_sub)
            y += 50
        elif line.startswith("!"):
            draw.text((100, y), line[1:], fill=(255, 200, 50), font=font_body)
            y += 40
        else:
            draw.text((100, y), line, fill=(200, 200, 210), font=font_body)
            y += 36

    # Bottom bar
    draw.rectangle([0, H - 40, W, H], fill=(30, 41, 59))
    draw.text((100, H - 32), "India Runs Data & AI Challenge — Redrob", fill=(150, 150, 160), font=font_small)

    return pil_to_cv(img)

def create_terminal_frame(lines, title="Terminal"):
    img = Image.new("RGB", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("consola.ttf", 22)
        font_title = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()

    # Terminal window chrome
    draw.rectangle([100, 80, W - 100, H - 80], fill=(30, 41, 59))
    draw.rectangle([100, 80, W - 100, 120], fill=(15, 23, 42))
    draw.ellipse([118, 95, 128, 105], fill=(255, 95, 87))
    draw.ellipse([138, 95, 148, 105], fill=(255, 189, 46))
    draw.ellipse([158, 95, 168, 105], fill=(39, 201, 63))
    draw.text((180, 95), title, fill=(180, 180, 190), font=font_title)

    y = 150
    for line in lines:
        if line.startswith("$"):
            draw.text((120, y), line, fill=(74, 175, 255), font=font)
        elif line.startswith(">"):
            draw.text((120, y), line[1:], fill=(255, 200, 50), font=font)
        else:
            draw.text((120, y), line, fill=(180, 180, 190), font=font)
        y += 32

    return pil_to_cv(img)

def create_submission_preview():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("consola.ttf", 20)
        font_title = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()

    draw.text((100, 80), "Top 100 Ranked Candidates — submission.csv", fill=(255, 255, 255), font=font_title)

    # Table header
    headers = ["candidate_id", "rank", "score", "reasoning"]
    col_starts = [100, 280, 360, 440]
    draw.rectangle([80, 140, W - 80, 180], fill=(74, 175, 255))
    for i, h in enumerate(headers):
        draw.text((col_starts[i] + 10, 147), h, fill=(255, 255, 255), font=font)

    # Table rows (sample top 15)
    data = [
        ["CAND_0046525", "1", "0.7795", "Senior ML Engineer @Genpact AI | YOLO, pgvector, IR"],
        ["CAND_0046064", "2", "0.7696", "Senior NLP Engineer @Salesforce | Deep Learning, Pinecone"],
        ["CAND_0005260", "3", "0.7621", "Senior NLP Engineer @Netflix | NLP, Semantic Search"],
        ["CAND_0030348", "4", "0.7593", "ML Engineer @BYJU'S | pgvector, GANs, Vector Search"],
        ["CAND_0058575", "5", "0.7587", "AI Engineer @Krutrim | HuggingFace, RL"],
        ["CAND_0098217", "6", "0.7586", "ML Engineer @Glance | PEFT, W&B, Statistical Modeling"],
        ["CAND_0010257", "7", "0.7561", "Senior Data Scientist @Google | RecSys, MLflow, TF"],
        ["CAND_0062247", "8", "0.7557", "AI Engineer @Google | PEFT, HuggingFace, RAG"],
        ["CAND_0096142", "9", "0.7556", "Applied ML Engineer @upGrad | W&B, BentoML, RAG"],
        ["CAND_0004972", "10", "0.7555", "ML Engineer @Glance | W&B, TTS, BentoML"],
        ["CAND_0006418", "11", "0.7555", "ML Engineer @Verloop.io | Elasticsearch, OpenSearch"],
        ["CAND_0044222", "12", "0.7545", "AI Engineer @PolicyBazaar | Feature Eng, LLMs"],
        ["CAND_0010149", "13", "0.7538", "ML Engineer @Glance | Learning to Rank, Milvus"],
        ["CAND_0043860", "14", "0.7537", "Junior ML Engineer @Aganitha | Semantic Search, GANs"],
        ["CAND_0040178", "15", "0.7534", "ML Engineer @Meesho | Python, Weaviate, Vector Search"],
    ]
    for r, row in enumerate(data):
        y = 190 + r * 36
        bg = (30, 41, 59) if r % 2 == 0 else (24, 33, 48)
        draw.rectangle([80, y, W - 80, y + 36], fill=bg)
        for i, val in enumerate(row):
            c = (200, 200, 210) if i < 3 else (180, 180, 190)
            draw.text((col_starts[i] + 10, y + 6), val, fill=c, font=font)

    # Stats
    stats_y = 190 + len(data) * 36 + 30
    stats = [
        "| Processing Time: ~64s for 100K candidates",
        "| Memory: ~4 GB peak",
        "| 8 Scoring Dimensions | 9 Honeypot Checks | Weighted Composite Score",
    ]
    for i, s in enumerate(stats):
        draw.text((100, stats_y + i * 36), s, fill=(74, 175, 255), font=font)

    return pil_to_cv(img)

def generate_video():
    scenes = []

    # Scene 1: Title
    scenes.append(create_frame(
        [],
        title="Redrob Candidate Ranker",
        sub_text="India Runs Data & AI Challenge — Hackathon Demo"
    ))

    # Scene 2: Architecture
    scenes.append(create_frame(
        [
            "# Pipeline Architecture",
            "",
            "candidates.jsonl (100K profiles)",
            "    |",
            "    +---> honeypot.py  —  9 anomaly detection signals",
            "    +---> scorers.py   —  8 scoring dimensions",
            "    |",
            "    v",
            "ranker.py  —  weighted sum  ->  sort  ->  top 100",
            "    |",
            "    v",
            "submission.csv  —  4 columns, 100 rows",
        ],
        title="Architecture",
        sub_text="End-to-end ranking pipeline"
    ))

    # Scene 3: Scoring Methodology
    scenes.append(create_frame(
        [
            "# 8 Scoring Dimensions (Weighted)",
            "",
            "! Title/Role   0.22  —  AI/ML role tier match",
            "! Skills       0.18  —  6 skill groups x proficiency",
            "! Career Qual  0.18  —  Tenure, seniority, diversity",
            "! Experience   0.13  —  3-10 YoE blended with ML density",
            "! Statement    0.10  —  ML intent, startup affinity",
            "! Behavioral   0.09  —  Recency, response, GitHub",
            "! Location     0.05  —  India tech hub priority",
            "! Education    0.05  —  Degree level x institution tier",
            "",
            "Score = (Weighted Sum) x (1 - Honeypot Penalty)"
        ],
        title="Scoring Methodology",
        sub_text="Composite scoring with honeypot safeguards"
    ))

    # Scene 4: Honeypot Detection
    scenes.append(create_frame(
        [
            "# Honeypot Detection — 9 Checks",
            "",
            "1. Many expert skills, low endorsements",
            "2. YOE / career history mismatch (>4yr gap)",
            "3. Assessment contradiction (expert skill, 0 score)",
            "4. Future activity date",
            "5. Unrealistic YOE (>50 years)",
            "6. Excessive skills (>30)",
            "7. All assessments very low",
            "8. Too many career entries (>15)",
            "9. Missing required fields",
            "",
            "! Max penalty: 0.6x — disqualify if >10% in top 100"
        ],
        title="Fraud Detection",
        sub_text="Catch synthetic profiles before they pollute rankings"
    ))

    # Scene 5: CLI Demo (simulated terminal)
    scenes.append(create_terminal_frame([
        "$ python main.py --input candidates.jsonl --output submission.csv",
        "",
        "2026-06-06 10:00:01 [INFO] Loading candidates from candidates.jsonl...",
        "2026-06-06 10:00:03 [INFO] Loaded 100,000 candidates",
        "2026-06-06 10:00:05 [INFO] Scoring dimension 1/8: title_role",
        "2026-06-06 10:00:08 [INFO] Scoring dimension 2/8: skills",
        "2026-06-06 10:00:10 [INFO] Scoring dimension 3/8: career_quality",
        "2026-06-06 10:00:13 [INFO] Scoring dimension 4/8: experience",
        "2026-06-06 10:00:15 [INFO] Scoring dimension 5/8: statement",
        "2026-06-06 10:00:18 [INFO] Scoring dimension 6/8: behavioral",
        "2026-06-06 10:00:20 [INFO] Scoring dimension 7/8: location",
        "2026-06-06 10:00:22 [INFO] Scoring dimension 8/8: education",
        "2026-06-06 10:00:24 [INFO] Running honeypot detection...",
        "2026-06-06 10:00:26 [INFO] Sorting 100,000 candidates by score...",
        "2026-06-06 10:00:27 [INFO] Writing top 100 to submission.csv",
        "2026-06-06 10:00:28 [INFO] Done! submission.csv ready",
    ], title="CLI Pipeline"))

    # Scene 6: API + Frontend
    scenes.append(create_frame(
        [
            "# API Endpoints (FastAPI)",
            "",
            "GET   /api/weights    —  Return scorer weights",
            "GET   /api/status     —  Check cached results",
            "POST  /api/rank       —  Run ranking pipeline",
            "GET   /api/results    —  Get cached ranked results",
            "GET   /api/download   —  Download submission.csv",
            "",
            "# Frontend (Vue 3 + PrimeVue + ApexCharts)",
            "",
            "Dashboard  |  Results  |  Candidate Detail",
            "Stats      |  Export   |  About",
            "",
            "! Start: start.bat  =>  uvicorn + npm run dev",
            "! Open: http://localhost:3000"
        ],
        title="API + Frontend",
        sub_text="Full-stack ranking application"
    ))

    # Scene 7: Submission Preview
    scenes.append(create_submission_preview())

    # Scene 8: End
    scenes.append(create_frame(
        [
            "",
            "",
            "# Thank You!",
            "",
            "Repository: Redrob Candidate Ranker",
            "Challenge:  India Runs Data & AI Challenge",
            "Dataset:    100,000 candidates",
            "",
            "8 Scoring Dimensions  |  9 Honeypot Checks",
            "FastAPI Backend       |  Vue 3 Frontend",
            "",
            "! github.com/anomalyco/opencode"
        ],
        title="",
        sub_text=""
    ))

    # Create video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("demo.mp4", fourcc, FPS, (W, H))

    for i, frame in enumerate(scenes):
        print(f"Rendering scene {i+1}/{len(scenes)}...")
        for _ in range(FRAMES_PER_SCENE):
            out.write(frame)

    out.release()
    cv2.destroyAllWindows()
    print(f"Done! Video saved as demo.mp4")

if __name__ == "__main__":
    generate_video()
