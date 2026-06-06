import csv
import io
import json
import os
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Redrob Candidate Ranker",
    page_icon="",
    layout="wide",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import SCORER_WEIGHTS
from ranker import score_candidate, load_candidates

DEFAULT_JSONL = r"[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"


def candidate_to_row(cand, rank):
    profile = cand.get("profile", {})
    s = cand.get("sub_scores", {})
    dim_map = {
        "title_role": "Title/Role",
        "skills": "Skills",
        "career_quality": "Career Quality",
        "experience": "Experience",
        "statement": "Statement",
        "behavioral": "Behavioral",
        "location": "Location",
        "education": "Education",
    }
    row = {
        "Rank": rank,
        "Candidate ID": cand["candidate_id"],
        "Name": profile.get("anonymized_name", ""),
        "Current Title": profile.get("current_title", ""),
        "Company": profile.get("current_company", ""),
        "Location": f"{profile.get('location', '')}, {profile.get('country', '')}",
        "YoE": profile.get("years_of_experience", 0),
        "Total Score": cand["score"],
        "Honeypot": cand["honeypot"]["is_honeypot"],
        "Honeypot Flags": "; ".join(cand["honeypot"]["flags"]),
    }
    for key, label in dim_map.items():
        row[label] = s.get(key, 0)
    return row


st.title("Redrob Hackathon — Candidate Ranker")
st.markdown(
    """
    Rank the top **100 candidates** from 100,000 profiles for a **Senior AI Engineer** role 
    at a Series A startup. Built for the India Runs Data & AI Challenge by Redrob.
    """
)

st.sidebar.header("Configuration")

uploaded = st.sidebar.file_uploader(
    "Upload candidates.jsonl (or use default)",
    type=["jsonl"],
)

use_default = st.sidebar.checkbox("Use default 100K dataset", value=True)

if uploaded is not None:
    use_default = False

top_k = st.sidebar.slider("Top K candidates", 10, 100, 100)

run_btn = st.sidebar.button("Run Ranking", type="primary", use_container_width=True)

tab_results, tab_stats, tab_raw, tab_about = st.tabs(
    ["Results", "Statistics", "Raw CSV", "About"]
)

if "results" not in st.session_state:
    st.session_state.results = None
if "candidates" not in st.session_state:
    st.session_state.candidates = None


def run_pipeline():
    if use_default:
        jsonl_path = Path(DEFAULT_JSONL)
        if not jsonl_path.exists():
            st.error(f"Default file not found: {jsonl_path.resolve()}")
            return
        st.info(f"Loading {jsonl_path} ...")
        candidates = load_candidates(str(jsonl_path))
    elif uploaded is not None:
        content = uploaded.read().decode("utf-8")
        candidates = [json.loads(line) for line in content.strip().split("\n") if line.strip()]
        st.info(f"Loaded {len(candidates)} candidates from uploaded file.")
    else:
        st.warning("Select a data source first.")
        return

    n = len(candidates)
    progress_bar = st.progress(0, text="Scoring candidates...")

    results = []
    start = time.time()
    for i, c in enumerate(candidates):
        r = score_candidate(c)
        results.append(r)
        if (i + 1) % max(1, n // 100) == 0 or i == n - 1:
            pct = (i + 1) / n
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            progress_bar.progress(
                pct,
                text=f"Scored {i+1}/{n} ({rate:.0f} cand/s)",
            )

    results.sort(key=lambda r: (-r["score"], r["candidate_id"]))
    top = results[:top_k]

    for rank, entry in enumerate(top, start=1):
        entry["_rank"] = rank

    st.session_state.results = top
    st.session_state.candidates = candidates

    progress_bar.empty()
    elapsed = time.time() - start
    st.sidebar.success(f"Done in {elapsed:.1f}s for {n} candidates")

    df = pd.DataFrame([candidate_to_row(r, r["_rank"]) for r in top])
    st.session_state.df = df


if run_btn:
    run_pipeline()

with tab_results:
    if st.session_state.results is not None:
        df = st.session_state.df

        st.subheader("Ranked Candidates")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            score_filter = st.slider("Min Total Score", 0.0, 1.0, 0.0, 0.01)
        with col2:
            title_filter = st.text_input("Title contains", "")
        with col3:
            loc_filter = st.text_input("Location contains", "")
        with col4:
            hide_honeypot = st.checkbox("Hide honeypot candidates", value=True)

        filtered = df[df["Total Score"] >= score_filter]
        if title_filter:
            filtered = filtered[
                filtered["Current Title"].str.contains(title_filter, case=False, na=False)
            ]
        if loc_filter:
            filtered = filtered[
                filtered["Location"].str.contains(loc_filter, case=False, na=False)
            ]
        if hide_honeypot:
            filtered = filtered[~filtered["Honeypot"]]

        display_cols = [
            "Rank", "Candidate ID", "Name", "Current Title", "Company",
            "Location", "YoE", "Total Score",
        ]
        st.dataframe(
            filtered[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total Score": st.column_config.NumberColumn(format="%.4f"),
                "YoE": st.column_config.NumberColumn(format="%.1f"),
            },
        )

        st.subheader("Candidate Detail")
        selected_id = st.selectbox(
            "Select a Candidate ID to inspect",
            options=df["Candidate ID"].tolist(),
        )

        if selected_id:
            row = df[df["Candidate ID"] == selected_id].iloc[0]
            results_dict = {
                r["candidate_id"]: r for r in st.session_state.results
            }
            detail = results_dict[selected_id]

            col_a, col_b = st.columns([1, 2])

            with col_a:
                st.markdown(
                    f"""
                    **Name:** {row['Name']}  
                    **Title:** {row['Current Title']}  
                    **Company:** {row['Company']}  
                    **Location:** {row['Location']}  
                    **Years Exp:** {row['YoE']}  
                    **Total Score:** {row['Total Score']:.4f}  
                    **Rank:** #{int(row['Rank'])}
                    """
                )
                if row["Honeypot"]:
                    st.error(f"Honeypot: {row['Honeypot Flags']}")

            with col_b:
                dimensions = list(SCORER_WEIGHTS.keys())
                sub_scores = [detail["sub_scores"].get(d, 0) for d in dimensions]
                weights = [SCORER_WEIGHTS.get(d, 0) for d in dimensions]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=sub_scores + [sub_scores[0]],
                    theta=[d.replace("_", " ").title() for d in dimensions] + [dimensions[0].replace("_", " ").title()],
                    fill="toself",
                    name="Score",
                    line_color="#00bcd4",
                ))
                fig.add_trace(go.Scatterpolar(
                    r=weights + [weights[0]],
                    theta=[d.replace("_", " ").title() for d in dimensions] + [dimensions[0].replace("_", " ").title()],
                    fill="toself",
                    name="Weight",
                    line_color="#ff9800",
                    opacity=0.3,
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 1]),
                    ),
                    height=350,
                    margin=dict(l=40, r=40, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.1),
                )
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Dimension breakdown"):
                dim_df = pd.DataFrame([
                    {
                        "Dimension": d.replace("_", " ").title(),
                        "Score": f"{detail['sub_scores'].get(d, 0):.4f}",
                        "Weight": f"{SCORER_WEIGHTS.get(d, 0):.2f}",
                        "Weighted": f"{detail['sub_scores'].get(d, 0) * SCORER_WEIGHTS.get(d, 0):.4f}",
                        "Reasoning": detail["reasonings"].get(d, ""),
                    }
                    for d in SCORER_WEIGHTS
                ])
                st.dataframe(dim_df, use_container_width=True, hide_index=True)

                hp = detail.get("honeypot", {})
                if hp.get("flags"):
                    st.warning(f"Honeypot flags: {', '.join(hp['flags'])} | Penalty: {hp['penalty']:.2f}")

    else:
        st.info("Click **Run Ranking** in the sidebar to start.")

with tab_stats:
    if st.session_state.results is not None:
        df = st.session_state.df

        st.subheader("Score Distribution")
        fig_hist = px.histogram(
            df, x="Total Score", nbins=30,
            title="Total Score Distribution (Top 100)",
            labels={"Total Score": "Score"},
            color_discrete_sequence=["#00bcd4"],
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("Dimension Scores Overview")
        dim_cols = [
            "Title/Role", "Skills", "Career Quality", "Experience",
            "Statement", "Behavioral", "Location", "Education",
        ]
        dim_df = df[dim_cols].describe().T.reset_index()
        dim_df.columns = ["Dimension", "Count", "Mean", "Std", "Min", "25%", "50%", "75%", "Max"]
        st.dataframe(dim_df, use_container_width=True, hide_index=True)

        st.subheader("Top Titles Distribution")
        title_counts = df["Current Title"].value_counts().head(15)
        fig_titles = px.bar(
            x=title_counts.values,
            y=title_counts.index,
            orientation="h",
            title="Top 15 Current Titles in Top 100",
            labels={"x": "Count", "y": "Title"},
            color=title_counts.values,
            color_continuous_scale="blues",
        )
        fig_titles.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_titles, use_container_width=True)

        st.subheader("Location Distribution")
        loc_counts = df["Location"].value_counts().head(10)
        fig_loc = px.pie(
            values=loc_counts.values,
            names=loc_counts.index,
            title="Top 10 Locations",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig_loc, use_container_width=True)

        st.subheader("YoE vs Score")
        fig_scatter = px.scatter(
            df, x="YoE", y="Total Score",
            hover_data=["Candidate ID", "Current Title"],
            title="Years of Experience vs Score",
            color="Total Score",
            color_continuous_scale="viridis",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        honeypot_count = df["Honeypot"].sum()
        if honeypot_count > 0:
            st.warning(f"Honeypot candidates in top {top_k}: {honeypot_count}")

    else:
        st.info("Run the ranking first.")

with tab_raw:
    if st.session_state.results is not None:
        df = st.session_state.df

        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        results_dict = {r["candidate_id"]: r for r in st.session_state.results}
        for _, row in df.iterrows():
            detail = results_dict[row["Candidate ID"]]
            writer.writerow([
                row["Candidate ID"],
                int(row["Rank"]),
                f"{row['Total Score']:.4f}",
                detail["reasoning_short"],
            ])
        csv_data = csv_buf.getvalue()

        st.download_button(
            label="Download Submission CSV",
            data=csv_data,
            file_name="submission.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )

        st.subheader("Preview")
        preview_df = pd.read_csv(io.StringIO(csv_data))
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
    else:
        st.info("Run the ranking first.")

with tab_about:
    st.markdown(
        """
        ### About

        **Redrob Hackathon** — India Runs Data & AI Challenge.

        **Job:** Senior AI Engineer at a Series A startup  
        **Candidates:** 100,000 profiles  
        **Output:** Top 100 ranked candidates

        #### Scoring Dimensions

        | Dimension | Weight | What it measures |
        |---|---|---|
        | Title/Role | 0.25 | Current title match against AI/ML role tiers |
        | Skills | 0.20 | Skill relevance to embeddings, vector DB, NLP, ML eval |
        | Career Quality | 0.20 | Tenure stability, career progression, production exposure |
        | Experience | 0.15 | Years of experience (ideal 3-10) + ML relevance |
        | Behavioral | 0.10 | Recency, response rate, verification, salary alignment |
        | Location | 0.05 | India preferred city, willingness to relocate |
        | Education | 0.05 | Degree level, institution tier, CS-related field |

        #### Honeypot Detection

        Profiles with impossible combinations (e.g. expert in 10 skills with 0 endorsements)
        are penalized automatically.

        #### Compute

        Pure Python, CPU only, no network calls — runs in under 5 min on 16GB RAM.
        """
    )
