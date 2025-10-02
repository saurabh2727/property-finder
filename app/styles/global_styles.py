"""
Global Design System - Domain/REA Inspired
Professional color palette and CSS styles
"""

# Color Palette
COLORS = {
    # Primary Brand
    'primary_blue': '#002F6C',
    'primary_teal': '#00A0AF',

    # Secondary
    'secondary_red': '#E4002B',
    'secondary_gold': '#F5A623',

    # Neutrals
    'dark_navy': '#001E3C',
    'slate_gray': '#4A5568',
    'medium_gray': '#718096',
    'light_gray': '#F7FAFC',
    'border_gray': '#E2E8F0',
    'white': '#FFFFFF',

    # Success/Info/Warning
    'success_green': '#38A169',
    'success_light': '#D4F4DD',
    'info_blue': '#3182CE',
    'info_light': '#EBF8FF',
    'warning_orange': '#DD6B20',
    'warning_light': '#FFF5E5',
}

# Gradients
GRADIENTS = {
    'primary': f"linear-gradient(135deg, {COLORS['primary_blue']} 0%, {COLORS['primary_teal']} 100%)",
    'card': f"linear-gradient(180deg, {COLORS['white']} 0%, {COLORS['light_gray']} 100%)",
    'header': f"linear-gradient(90deg, {COLORS['dark_navy']} 0%, {COLORS['primary_blue']} 100%)",
}

def get_global_css():
    """Returns comprehensive CSS for professional real estate UI"""
    return f"""
    <style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@600;700&display=swap');

    /* Global Resets and Base Styles */
    * {{
        box-sizing: border-box;
    }}

    /* Typography */
    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {COLORS['dark_navy']};
        line-height: 1.6;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', 'Inter', sans-serif;
        color: {COLORS['dark_navy']};
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}

    h1 {{ font-size: 2.5rem; }}
    h2 {{ font-size: 2rem; }}
    h3 {{ font-size: 1.5rem; }}

    /* Streamlit Container Improvements */
    .main .block-container {{
        max-width: 1200px;
        padding-top: 0rem !important;
        padding-bottom: 3rem;
    }}

    /* Property Card Component */
    .property-card {{
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid {COLORS['border_gray']};
        margin-bottom: 1.5rem;
    }}

    .property-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
        border-color: {COLORS['primary_teal']};
    }}

    .property-card-image {{
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-bottom: 1px solid {COLORS['border_gray']};
    }}

    .property-card-content {{
        padding: 1.5rem;
    }}

    .property-card-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {COLORS['dark_navy']};
        margin: 0 0 0.5rem 0;
    }}

    .property-card-location {{
        color: {COLORS['slate_gray']};
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }}

    /* Metric Cards */
    .metric-card {{
        background: {GRADIENTS['card']};
        border-left: 4px solid {COLORS['primary_teal']};
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }}

    .metric-card:hover {{
        transform: translateX(4px);
    }}

    .metric-card h4 {{
        margin: 0 0 0.5rem 0;
        color: {COLORS['dark_navy']};
        font-size: 1.1rem;
    }}

    .metric-card p {{
        margin: 0;
        color: {COLORS['slate_gray']};
        font-size: 0.9rem;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
        line-height: 1.2;
    }}

    .badge-success {{
        background: {COLORS['success_light']};
        color: #22543D;
    }}

    .badge-info {{
        background: {COLORS['info_light']};
        color: #1E3A8A;
    }}

    .badge-warning {{
        background: {COLORS['warning_light']};
        color: #7C2D12;
    }}

    .badge-primary {{
        background: {COLORS['primary_blue']};
        color: white;
    }}

    /* Buttons */
    .btn-primary {{
        background: {GRADIENTS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-block;
        font-size: 1rem;
    }}

    .btn-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 47, 108, 0.3);
    }}

    .btn-secondary {{
        background: white;
        color: {COLORS['primary_blue']};
        border: 2px solid {COLORS['primary_blue']};
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }}

    .btn-secondary:hover {{
        background: {COLORS['primary_blue']};
        color: white;
    }}

    /* Hero Section */
    .hero-section {{
        background: {GRADIENTS['header']};
        color: white;
        padding: 3rem 2rem;
        border-radius: 0px;
        margin-top: 0rem !important;
        margin-bottom: 2rem;
        text-align: center;
    }}

    .hero-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        color: white;
    }}

    .hero-subtitle {{
        font-size: 1.25rem;
        opacity: 0.9;
        margin: 0;
    }}

    /* Price Display */
    .price {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLORS['primary_blue']};
        font-family: 'Inter', monospace;
    }}

    .price-label {{
        font-size: 0.875rem;
        color: {COLORS['medium_gray']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Stats Grid */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }}

    .stat-box {{
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid {COLORS['border_gray']};
        text-align: center;
    }}

    .stat-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary_blue']};
        margin: 0;
    }}

    .stat-label {{
        font-size: 0.875rem;
        color: {COLORS['medium_gray']};
        margin-top: 0.25rem;
    }}

    /* Investment Score Bar */
    .score-bar {{
        width: 100%;
        height: 8px;
        background: {COLORS['border_gray']};
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }}

    .score-bar-fill {{
        height: 100%;
        background: {GRADIENTS['primary']};
        transition: width 0.5s ease;
    }}

    /* Feature List */
    .feature-list {{
        list-style: none;
        padding: 0;
        margin: 0;
    }}

    .feature-item {{
        padding: 0.75rem 0;
        border-bottom: 1px solid {COLORS['border_gray']};
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .feature-item:last-child {{
        border-bottom: none;
    }}

    .feature-icon {{
        width: 24px;
        height: 24px;
        flex-shrink: 0;
    }}

    /* Alert Boxes */
    .alert {{
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }}

    .alert-success {{
        background: {COLORS['success_light']};
        border-color: {COLORS['success_green']};
        color: #22543D;
    }}

    .alert-info {{
        background: {COLORS['info_light']};
        border-color: {COLORS['info_blue']};
        color: #1E3A8A;
    }}

    .alert-warning {{
        background: {COLORS['warning_light']};
        border-color: {COLORS['warning_orange']};
        color: #7C2D12;
    }}

    /* Dividers */
    .divider {{
        height: 1px;
        background: {COLORS['border_gray']};
        margin: 2rem 0;
    }}

    /* Skeleton Loading */
    .skeleton {{
        background: linear-gradient(90deg, {COLORS['light_gray']} 25%, #E9ECEF 50%, {COLORS['light_gray']} 75%);
        background-size: 200% 100%;
        animation: loading 1.5s ease-in-out infinite;
        border-radius: 4px;
    }}

    @keyframes loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}

    /* Streamlit Widget Overrides */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}

    /* Hide Streamlit Branding (Optional) */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Improve Expander Styling */
    .streamlit-expanderHeader {{
        font-weight: 700;
        font-size: 1.1rem;
        color: {COLORS['dark_navy']};
        border-radius: 8px;
        background: {COLORS['light_gray']};
        padding: 0.75rem 1rem;
    }}

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }}

    /* Responsive Design */
    @media (max-width: 768px) {{
        h1 {{ font-size: 2rem; }}
        h2 {{ font-size: 1.5rem; }}

        .hero-title {{ font-size: 1.75rem; }}
        .hero-subtitle {{ font-size: 1rem; }}

        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}
    </style>
    """
