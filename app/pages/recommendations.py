import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from styles.global_styles import get_global_css, COLORS
from components.property_card import render_hero_section
from utils.session_state import update_workflow_step, save_recommendations, render_workflow_progress
from models.hybrid_recommender import (
    HybridRecommender, DIMENSIONS, DIM_LABELS, MODE_WEIGHTS, infer_mode,
)


# ── Page entry point ──────────────────────────────────────────────────────────

def render_recommendations_page():
    st.markdown(get_global_css(), unsafe_allow_html=True)
    render_hero_section(
        title="🎯 Suburb Recommendations",
        subtitle="Hybrid scoring: suburb intelligence + content similarity + LLM insights",
    )
    render_workflow_progress(current_step=3)
    st.markdown("---")

    if not _check_prerequisites():
        return

    df             = st.session_state.suburb_data
    profile        = st.session_state.customer_profile

    if st.session_state.get('recommendations') is not None:
        _display_existing(df, profile)
    else:
        _generate_flow(df, profile)


# ── Pre-requisite check ───────────────────────────────────────────────────────

def _check_prerequisites() -> bool:
    if not st.session_state.get('profile_generated', False):
        st.warning("Please complete customer profiling first.")
        if st.button("← Customer Profile"):
            st.session_state.current_page = 'customer_profile'
            st.rerun()
        return False
    if not st.session_state.get('data_uploaded', False):
        st.warning("Please upload or fetch suburb data first.")
        if st.button("← Data Upload"):
            st.session_state.current_page = 'data_upload'
            st.rerun()
        return False
    return True


# ── Main generation flow ──────────────────────────────────────────────────────

def _generate_flow(df: pd.DataFrame, profile: dict):
    recommender = HybridRecommender()

    # ── Step 1: Data coverage summary ────────────────────────────────────────
    coverage = recommender.dimension_coverage(df)
    with st.expander("📊 Data Coverage by Dimension", expanded=False):
        cov_df = pd.DataFrame([
            {"Dimension": DIM_LABELS[d], "Columns available": n,
             "Status": "✅ Good" if n >= 2 else ("⚠️ Limited" if n == 1 else "❌ No data")}
            for d, n in coverage.items()
        ])
        st.dataframe(cov_df, use_container_width=True, hide_index=True)
        if all(n == 0 for n in coverage.values()):
            st.warning("No enrichment data found. Fetch API sources on the Data Upload page for better results.")

    st.markdown("---")

    # ── Step 2: Mode + weight configuration ──────────────────────────────────
    st.markdown("### Configure Recommendation")

    col_mode, col_top_n = st.columns([3, 1])
    with col_mode:
        auto_mode = infer_mode(profile)
        mode = st.selectbox(
            "Buyer / Investor Mode",
            options=recommender.available_modes(),
            index=recommender.available_modes().index(auto_mode),
            help=f"Auto-detected from your profile: **{auto_mode}**",
        )
    with col_top_n:
        top_n = st.number_input("# Suburbs", min_value=3, max_value=30, value=10, step=1)

    # Weight sliders — pre-filled from selected mode, adjustable
    st.markdown("#### Dimension Weights")
    st.caption("Adjust how much each dimension matters. Values are automatically normalized.")

    preset = recommender.weights_for_mode(mode)
    weights = {}
    slider_cols = st.columns(len(DIMENSIONS))
    for col, dim in zip(slider_cols, DIMENSIONS):
        with col:
            weights[dim] = st.slider(
                DIM_LABELS[dim],
                0.0, 1.0,
                value=float(preset[dim]),
                step=0.05,
                key=f"w_{dim}",
            )

    # Normalize and show totals
    total_w = sum(weights.values())
    if total_w > 0:
        norm_weights = {k: v / total_w for k, v in weights.items()}
    else:
        norm_weights = preset
        st.warning("All weights are zero — using mode defaults.")

    with st.expander("Effective weights (normalized)", expanded=False):
        st.json({DIM_LABELS[d]: f"{w:.0%}" for d, w in norm_weights.items()})

    # ── Step 3: Optional LLM intent parsing ──────────────────────────────────
    st.markdown("---")
    st.markdown("#### LLM Intent (optional)")
    st.caption("Describe what matters to you in plain English. The AI will adjust the weights above.")

    intent_query = st.text_input(
        "What are you looking for?",
        placeholder='e.g. "quiet area, good for kids, close to trains, not too expensive"',
        key="intent_query",
    )
    use_llm_weights = False
    llm_weights = None
    if intent_query:
        api_key = st.session_state.get('user_openai_api_key')
        if api_key:
            if st.button("🧠 Extract weights from intent"):
                with st.spinner("Asking AI to interpret your intent…"):
                    from services.openai_service import OpenAIService
                    try:
                        svc = OpenAIService(api_key=api_key)
                        llm_weights = svc.extract_intent_weights(intent_query, profile)
                        if llm_weights:
                            st.session_state['llm_weights'] = llm_weights
                            st.success("Weights updated from your description.")
                    except Exception as e:
                        st.warning(f"LLM weight extraction failed: {e}")
        else:
            st.caption("Add your OpenAI API key in the sidebar to enable LLM intent parsing.")

    if st.session_state.get('llm_weights'):
        llm_weights = st.session_state['llm_weights']
        use_llm_weights = st.checkbox(
            "Use AI-extracted weights instead of sliders",
            value=True,
            key="use_llm_weights",
        )
        if use_llm_weights:
            st.markdown("**AI-extracted weights:**")
            st.json({DIM_LABELS[d]: f"{llm_weights.get(d, 0):.0%}" for d in DIMENSIONS})

    final_weights = llm_weights if (use_llm_weights and llm_weights) else norm_weights

    # ── Step 4: Generate ─────────────────────────────────────────────────────
    st.markdown("---")
    budget = profile.get('property_preferences', {}).get('price_range', {})
    if budget.get('min') and budget.get('max'):
        st.info(f"Budget filter: ${float(str(budget['min']).replace('$','').replace(',','')):,.0f}"
                f" – ${float(str(budget['max']).replace('$','').replace(',','')):,.0f} (±20% buffer)")

    if st.button("🚀 Generate Recommendations", type="primary", use_container_width=True):
        with st.spinner("Running hybrid scoring pipeline…"):
            result_df = recommender.recommend(df, profile, weights=final_weights, top_n=top_n)

        if result_df.empty:
            st.error("No suburbs matched. Try relaxing your budget filter or fetching more data.")
            return

        # Optional LLM explanations
        explanations = {}
        api_key = st.session_state.get('user_openai_api_key')
        if api_key:
            with st.spinner("Generating AI explanations…"):
                try:
                    from services.openai_service import OpenAIService
                    svc = OpenAIService(api_key=api_key)
                    explanations = svc.generate_suburb_explanations(
                        result_df, final_weights, profile, top_n=min(top_n, 10)
                    )
                except Exception:
                    pass  # explanations are optional

        recs_data = {
            'primary_recommendations': result_df,
            'recommendation_engine':   'hybrid',
            'weights_used':            final_weights,
            'mode':                    mode,
            'explanations':            explanations,
        }
        save_recommendations(recs_data)
        update_workflow_step(4)
        st.rerun()


# ── Display existing recommendations ─────────────────────────────────────────

def _display_existing(df: pd.DataFrame, profile: dict):
    recs = st.session_state.recommendations
    top_suburbs = recs.get('primary_recommendations')
    engine = recs.get('recommendation_engine', 'unknown')
    weights = recs.get('weights_used', {})
    mode = recs.get('mode', '')
    explanations = recs.get('explanations', {})

    if top_suburbs is None or (isinstance(top_suburbs, pd.DataFrame) and top_suburbs.empty):
        st.warning("No recommendations stored. Please regenerate.")
        if st.button("🔄 Regenerate"):
            st.session_state.recommendations = None
            st.rerun()
        return

    # Action bar
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.recommendations = None
            if 'llm_weights' in st.session_state:
                del st.session_state['llm_weights']
            st.rerun()
    with col2:
        if st.button("➡️ Generate Reports", type="primary", use_container_width=True):
            st.session_state.current_page = 'reports'
            update_workflow_step(5)
            st.rerun()
    with col3:
        engine_label = {
            'hybrid':     '🧠 Hybrid (Suburb Intelligence)',
            'ai_genai':   '🤖 AI/GenAI',
            'rule_based': '📊 Rule-Based',
        }.get(engine, engine)
        st.info(f"Engine: {engine_label}  |  Mode: {mode}")

    st.markdown("---")

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        avg_price = pd.to_numeric(top_suburbs.get('Median Price', pd.Series()), errors='coerce').mean()
        st.metric("Avg Price", f"${avg_price:,.0f}" if not np.isnan(avg_price) else "N/A")
    with c2:
        avg_yield = pd.to_numeric(top_suburbs.get('Rental Yield on Houses', pd.Series()), errors='coerce').mean()
        st.metric("Avg Yield", f"{avg_yield:.1f}%" if not np.isnan(avg_yield) else "N/A")
    with c3:
        avg_score = pd.to_numeric(top_suburbs.get('final_score', pd.Series()), errors='coerce').mean()
        st.metric("Avg Score", f"{avg_score:.2f}" if not np.isnan(avg_score) else "N/A")
    with c4:
        n_states = top_suburbs['State'].nunique() if 'State' in top_suburbs.columns else 0
        st.metric("States", n_states)

    st.markdown("---")

    # Display tabs
    tab1, tab2, tab3 = st.tabs(["🏆 Ranked List", "📡 Dimension Breakdown", "🕸️ Radar Comparison"])

    with tab1:
        _render_ranked_list(top_suburbs, explanations, weights)

    with tab2:
        _render_dimension_breakdown(top_suburbs, weights)

    with tab3:
        _render_radar_comparison(top_suburbs)


# ── Ranked list ───────────────────────────────────────────────────────────────

def _render_ranked_list(df: pd.DataFrame, explanations: dict, weights: dict):
    suburb_col = 'Suburb' if 'Suburb' in df.columns else df.columns[0]

    for rank, (_, row) in enumerate(df.iterrows(), 1):
        name  = row.get(suburb_col, 'Unknown')
        state = row.get('State', '')
        score = row.get('final_score', 0)
        price = row.get('Median Price')
        yld   = row.get('Rental Yield on Houses')
        growth = row.get('10 yr Avg. Annual Growth')

        score_pct = int(score * 100)
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"

        with st.expander(
            f"{medal} **{name}**, {state}  —  Score: {score:.3f}",
            expanded=(rank <= 3),
        ):
            col_metrics, col_dims = st.columns([1, 2])

            with col_metrics:
                st.markdown(f"**Final Score:** {score:.3f}")
                if price:
                    try:
                        st.markdown(f"**Median Price:** ${float(price):,.0f}")
                    except Exception:
                        pass
                if yld:
                    try:
                        st.markdown(f"**Rental Yield:** {float(yld):.1f}%")
                    except Exception:
                        pass
                if growth:
                    try:
                        st.markdown(f"**10yr Growth:** {float(growth):.1f}%")
                    except Exception:
                        pass

                # Score breakdown
                s_score = row.get('suburb_score', None)
                c_sim   = row.get('content_similarity', None)
                p_align = row.get('preference_alignment', None)
                if s_score is not None:
                    st.markdown("---")
                    st.caption("Score components:")
                    st.caption(f"  Suburb score: {s_score:.2f}")
                    st.caption(f"  Content sim:  {c_sim:.2f}")
                    st.caption(f"  Pref align:   {p_align:.2f}")

            with col_dims:
                # Dimension score bars
                dim_rows = []
                for dim in DIMENSIONS:
                    col_name = f'{dim}_dim_score'
                    if col_name in row:
                        w = weights.get(dim, 0)
                        dim_rows.append({
                            'Dimension': DIM_LABELS[dim],
                            'Score': round(float(row[col_name]), 2),
                            'Weight': f"{w:.0%}",
                        })
                if dim_rows:
                    dim_df = pd.DataFrame(dim_rows)
                    fig = px.bar(
                        dim_df, x='Score', y='Dimension', orientation='h',
                        range_x=[0, 1],
                        color='Score',
                        color_continuous_scale='RdYlGn',
                        height=220,
                        text='Score',
                    )
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=0, b=0),
                        coloraxis_showscale=False,
                        showlegend=False,
                    )
                    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

            # LLM explanation
            explanation = explanations.get(name)
            if explanation:
                st.info(f"💬 {explanation}")


# ── Dimension breakdown table ─────────────────────────────────────────────────

def _render_dimension_breakdown(df: pd.DataFrame, weights: dict):
    suburb_col = 'Suburb' if 'Suburb' in df.columns else df.columns[0]
    dim_cols = {dim: f'{dim}_dim_score' for dim in DIMENSIONS if f'{dim}_dim_score' in df.columns}

    if not dim_cols:
        st.info("No dimension scores available.")
        return

    # Build display table
    rows = []
    for _, row in df.iterrows():
        r = {'Suburb': row.get(suburb_col, ''), 'State': row.get('State', '')}
        for dim, col in dim_cols.items():
            r[DIM_LABELS[dim]] = round(float(row[col]), 2)
        r['Final Score'] = round(float(row.get('final_score', 0)), 3)
        rows.append(r)

    table_df = pd.DataFrame(rows)

    st.markdown("**Active weights:**  " + "  ·  ".join(
        f"{DIM_LABELS[d]} {w:.0%}" for d, w in weights.items() if w > 0
    ))

    st.dataframe(
        table_df.style.background_gradient(
            subset=[DIM_LABELS[d] for d in dim_cols],
            cmap='RdYlGn', vmin=0, vmax=1,
        ).background_gradient(subset=['Final Score'], cmap='Blues', vmin=0, vmax=1),
        use_container_width=True,
        hide_index=True,
    )


# ── Radar comparison chart ────────────────────────────────────────────────────

def _render_radar_comparison(df: pd.DataFrame):
    suburb_col = 'Suburb' if 'Suburb' in df.columns else df.columns[0]
    dim_cols = [f'{d}_dim_score' for d in DIMENSIONS if f'{d}_dim_score' in df.columns]
    dim_labels = [DIM_LABELS[d] for d in DIMENSIONS if f'{d}_dim_score' in df.columns]

    if len(dim_cols) < 3:
        st.info("Need at least 3 dimension scores for radar chart.")
        return

    top5 = df.head(5)
    names = [str(r.get(suburb_col, f'Suburb {i}')) for i, (_, r) in enumerate(top5.iterrows())]

    selected = st.multiselect(
        "Select suburbs to compare (max 5)",
        options=names,
        default=names[:min(3, len(names))],
    )

    if not selected:
        return

    fig = go.Figure()
    categories = dim_labels + [dim_labels[0]]  # close the polygon

    for name in selected:
        row = top5[top5[suburb_col].astype(str) == name]
        if row.empty:
            continue
        row = row.iloc[0]
        values = [float(row.get(c, 0.5)) for c in dim_cols] + [float(row.get(dim_cols[0], 0.5))]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=name,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
