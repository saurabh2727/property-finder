"""
Property Card Component - Domain/REA Inspired Design
Beautiful, professional property listing cards
"""
import streamlit as st
from typing import Dict, Optional

def render_property_card(
    suburb_name: str,
    state: str,
    median_price: float,
    rental_yield: float,
    investment_score: Optional[float] = None,
    growth_rate: Optional[float] = None,
    distance_cbd: Optional[float] = None,
    features: Optional[Dict] = None,
    rank: Optional[int] = None,
    show_image: bool = True
):
    """
    Render a professional property card

    Args:
        suburb_name: Name of suburb
        state: State abbreviation
        median_price: Median property price
        rental_yield: Rental yield percentage
        investment_score: Investment score out of 10
        growth_rate: Annual growth rate percentage
        distance_cbd: Distance to CBD in km
        features: Dict of additional features
        rank: Ranking number (optional)
        show_image: Whether to show suburb image
    """

    # Generate image URL (using Unsplash for now, can be replaced)
    image_url = f"https://source.unsplash.com/800x400/?{suburb_name},australia,property" if show_image else None

    # Determine badge based on score or rank
    badge_html = ""
    if rank == 1:
        badge_html = '<span class="badge badge-primary">🏆 Top Pick</span>'
    elif investment_score and investment_score >= 8.5:
        badge_html = '<span class="badge badge-success">⭐ Excellent</span>'
    elif investment_score and investment_score >= 7.5:
        badge_html = '<span class="badge badge-info">✓ Good Value</span>'

    # Build feature icons
    feature_icons = []
    if features:
        if features.get('school_rating'):
            feature_icons.append(f"🎓 Schools: {features['school_rating']}/10")
        if features.get('transport_score'):
            feature_icons.append(f"🚊 Transport: {features['transport_score']}/10")
        if features.get('vacancy_rate'):
            feature_icons.append(f"📊 Vacancy: {features['vacancy_rate']}%")

    # Score bar width
    score_width = int((investment_score or 0) * 10) if investment_score else 0

    card_html = f"""
    <div class="property-card">
        {"<img src='" + image_url + "' class='property-card-image' alt='" + suburb_name + "' onerror='this.style.display=\"none\"'>" if show_image else ""}

        <div class="property-card-content">
            <!-- Header with Title and Badge -->
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                <h3 class="property-card-title">{suburb_name}</h3>
                {badge_html}
            </div>

            <!-- Location Info -->
            <div class="property-card-location">
                <span>📍 {state}</span>
                {f"<span style='margin-left: 1rem;'>🏙️ {distance_cbd:.1f}km to CBD</span>" if distance_cbd else ""}
            </div>

            <!-- Price and Yield Grid -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.25rem 0; padding: 1rem; background: #F7FAFC; border-radius: 8px;">
                <div>
                    <div class="price-label">Median Price</div>
                    <div class="price">${median_price:,.0f}</div>
                </div>
                <div>
                    <div class="price-label">Rental Yield</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: #38A169;">
                        {rental_yield:.1f}%
                    </div>
                </div>
            </div>

            <!-- Investment Score -->
            {f'''
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600; color: #001E3C;">Investment Score</span>
                    <span style="font-weight: 700; font-size: 1.25rem; color: #002F6C;">{investment_score:.1f}/10</span>
                </div>
                <div class="score-bar">
                    <div class="score-bar-fill" style="width: {score_width}%;"></div>
                </div>
            </div>
            ''' if investment_score else ''}

            <!-- Growth Rate -->
            {f'''
            <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.75rem 0;">
                <span style="color: #718096;">📈 Growth:</span>
                <span style="font-weight: 600; color: {"#38A169" if growth_rate and growth_rate > 5 else "#718096"};">
                    {growth_rate:.1f}% p.a.
                </span>
            </div>
            ''' if growth_rate else ''}

            <!-- Feature Icons -->
            {f'''
            <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #E2E8F0;">
                {"".join([f'<span style="font-size: 0.85rem; color: #4A5568;">{icon}</span>' for icon in feature_icons])}
            </div>
            ''' if feature_icons else ''}
        </div>
    </div>
    """

    # Use st.html() if available (newer Streamlit versions), otherwise st.markdown()
    try:
        st.html(card_html)
    except AttributeError:
        st.markdown(card_html, unsafe_allow_html=True)


def render_compact_property_card(suburb_data: Dict, rank: Optional[int] = None):
    """
    Render a compact version of property card from DataFrame row

    Args:
        suburb_data: Dictionary with suburb information
        rank: Optional ranking number
    """
    features = {}

    # Extract features if available
    if 'School Rating' in suburb_data:
        features['school_rating'] = suburb_data['School Rating']
    if 'Public Transport Score' in suburb_data:
        features['transport_score'] = suburb_data['Public Transport Score']
    if 'Vacancy Rate' in suburb_data:
        features['vacancy_rate'] = suburb_data['Vacancy Rate']

    render_property_card(
        suburb_name=suburb_data.get('Suburb', 'Unknown'),
        state=suburb_data.get('State', ''),
        median_price=suburb_data.get('Median Price', 0),
        rental_yield=suburb_data.get('Rental Yield on Houses', 0),
        investment_score=suburb_data.get('Investment Score'),
        growth_rate=suburb_data.get('10 yr Avg. Annual Growth'),
        distance_cbd=suburb_data.get('Distance from CBD (km)'),
        features=features if features else None,
        rank=rank
    )


def render_comparison_cards(suburbs_list: list):
    """
    Render multiple property cards in a comparison layout

    Args:
        suburbs_list: List of suburb data dictionaries
    """
    cols = st.columns(min(len(suburbs_list), 3))

    for idx, (col, suburb) in enumerate(zip(cols, suburbs_list)):
        with col:
            render_compact_property_card(suburb, rank=idx+1 if idx < 3 else None)


def render_hero_section(title: str, subtitle: str):
    """Render a hero section for page headers"""
    st.markdown(f"""
    <div class="hero-section">
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_grid(metrics: list):
    """
    Render a grid of metric cards

    Args:
        metrics: List of dicts with 'label', 'value', 'icon' keys
    """
    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="stat-box">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{metric.get('icon', '📊')}</div>
                <div class="stat-value">{metric['value']}</div>
                <div class="stat-label">{metric['label']}</div>
            </div>
            """, unsafe_allow_html=True)
