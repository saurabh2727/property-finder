import streamlit as st

def apply_professional_styles():
    """Apply modern, Domain-style professional styling to the app"""

    st.markdown("""
    <style>
    /* Modern color palette inspired by Domain */
    :root {
        --primary-color: #00a86b;
        --primary-dark: #008854;
        --secondary-color: #2c3e50;
        --accent-color: #3498db;
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --error-color: #e74c3c;
        --text-dark: #2c3e50;
        --text-light: #7f8c8d;
        --bg-light: #ffffff;
        --bg-gray: #f8f9fa;
        --bg-dark: #2c3e50;
        --border-light: #ecf0f1;
        --shadow-light: rgba(0, 0, 0, 0.1);
        --shadow-medium: rgba(0, 0, 0, 0.15);
        --gradient-primary: linear-gradient(135deg, #00a86b 0%, #3498db 100%);
        --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global reset and modern base styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}

    /* Compact main content area - remove excessive padding */
    .main .block-container {
        padding: 1rem 1.5rem;
        max-width: 1400px;
        background: var(--bg-light);
    }

    /* Remove top and bottom margins from main content */
    .main {
        padding-top: 0;
        padding-bottom: 0;
    }

    /* Reduce spacing in containers */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Compact sections */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    /* Modern typography */
    h1 {
        color: var(--text-dark);
        font-weight: 700;
        font-size: 2.5rem;
        line-height: 1.2;
        margin-bottom: 1rem;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2 {
        color: var(--text-dark);
        font-weight: 600;
        font-size: 1.875rem;
        line-height: 1.3;
        margin-bottom: 1rem;
    }

    h3 {
        color: var(--text-dark);
        font-weight: 600;
        font-size: 1.5rem;
        line-height: 1.4;
        margin-bottom: 0.75rem;
    }

    /* Modern paragraph styling */
    p {
        color: var(--text-light);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    /* Remove excessive spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }

    /* Modern button styles */
    .stButton > button {
        background: var(--bg-light);
        border: 2px solid var(--border-light);
        border-radius: 12px;
        color: var(--text-dark);
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 4px var(--shadow-light);
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        background: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px var(--shadow-medium);
    }

    /* Force white text on all hovered buttons */
    .stButton > button:hover *,
    .stButton > button:hover span,
    .stButton > button:hover div {
        color: white !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--primary-color) !important;
        border: 2px solid var(--primary-color) !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Force white text on primary buttons - multiple selectors */
    .stButton > button[kind="primary"] *,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div,
    button[kind="primary"],
    button[kind="primary"] *,
    button[kind="primary"] span {
        color: white !important;
    }

    /* Additional targeting for Streamlit button text */
    .stButton button[data-testid="baseButton-primary"],
    .stButton button[data-testid="baseButton-primary"] *,
    .stButton button[data-testid="baseButton-primary"] span {
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 168, 107, 0.3);
    }

    /* Ensure active/selected buttons have white text */
    .stButton > button:active,
    .stButton > button:focus {
        background: var(--primary-color) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
    }

    /* Force white text on all active/focused buttons */
    .stButton > button:active *,
    .stButton > button:active span,
    .stButton > button:active div,
    .stButton > button:focus *,
    .stButton > button:focus span,
    .stButton > button:focus div {
        color: white !important;
    }

    .stButton > button[kind="primary"]:active,
    .stButton > button[kind="primary"]:focus {
        background: var(--primary-dark) !important;
        color: white !important;
        border-color: var(--primary-dark) !important;
    }

    /* Force white text on primary active/focused buttons */
    .stButton > button[kind="primary"]:active *,
    .stButton > button[kind="primary"]:active span,
    .stButton > button[kind="primary"]:active div,
    .stButton > button[kind="primary"]:focus *,
    .stButton > button[kind="primary"]:focus span,
    .stButton > button[kind="primary"]:focus div {
        color: white !important;
    }

    /* Button animations */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    /* Clean metrics */
    .metric-container {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* Clean expanders */
    .streamlit-expanderHeader {
        background-color: var(--gray-50);
        border: 1px solid var(--gray-200);
        border-radius: 6px;
        font-weight: 500;
    }

    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: var(--gray-50);
        border-radius: 6px;
        padding: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 4px;
        color: var(--gray-600);
        font-weight: 500;
        padding: 0.5rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: var(--primary-color);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Modern sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--bg-light) 0%, var(--bg-gray) 100%);
        border-right: 1px solid var(--border-light);
        box-shadow: 2px 0 10px var(--shadow-light);
    }

    /* Modern sidebar content */
    .css-1d391kg .stMarkdown {
        padding: 0.5rem;
    }

    /* Sidebar navigation enhancements */
    .css-1d391kg .stButton > button {
        border-radius: 10px;
        margin: 0.25rem 0;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    .css-1d391kg .stButton > button:hover {
        background: var(--primary-color) !important;
        color: white !important;
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(0, 168, 107, 0.3);
    }

    /* Force white text on sidebar buttons when hovered */
    .css-1d391kg .stButton > button:hover *,
    .css-1d391kg .stButton > button:hover span,
    .css-1d391kg .stButton > button:hover div {
        color: white !important;
    }

    /* Force white text on sidebar buttons when active/focused */
    .css-1d391kg .stButton > button:active,
    .css-1d391kg .stButton > button:focus {
        background: var(--primary-color) !important;
        color: white !important;
    }

    .css-1d391kg .stButton > button:active *,
    .css-1d391kg .stButton > button:active span,
    .css-1d391kg .stButton > button:active div,
    .css-1d391kg .stButton > button:focus *,
    .css-1d391kg .stButton > button:focus span,
    .css-1d391kg .stButton > button:focus div {
        color: white !important;
    }

    /* Modern form inputs */
    .stSelectbox > div > div {
        border: 2px solid var(--border-light);
        border-radius: 12px;
        background: var(--bg-light);
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px var(--shadow-light);
    }

    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 168, 107, 0.1);
    }

    .stTextInput > div > div > input {
        border: 2px solid var(--border-light);
        border-radius: 12px;
        background: var(--bg-light);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px var(--shadow-light);
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 168, 107, 0.1);
        outline: none;
    }

    .stTextArea > div > div > textarea {
        border: 2px solid var(--border-light);
        border-radius: 12px;
        background: var(--bg-light);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px var(--shadow-light);
    }

    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 168, 107, 0.1);
        outline: none;
    }

    /* Clean dataframes */
    .dataframe {
        border: 1px solid var(--gray-200);
        border-radius: 6px;
    }

    /* Clean progress bars */
    .stProgress .st-bo {
        background-color: var(--gray-200);
        border-radius: 4px;
    }

    .stProgress .st-bp {
        background-color: var(--primary-color);
        border-radius: 4px;
    }

    /* Remove emoji clutter from success/info/warning/error messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 6px;
        border-left: 4px solid;
        padding: 0.75rem 1rem;
    }

    .stSuccess {
        background-color: #f0fdf4;
        border-color: var(--success-color);
        color: #14532d;
    }

    .stInfo {
        background-color: #eff6ff;
        border-color: var(--primary-color);
        color: #1e3a8a;
    }

    .stWarning {
        background-color: #fffbeb;
        border-color: var(--warning-color);
        color: #92400e;
    }

    .stError {
        background-color: #fef2f2;
        border-color: var(--error-color);
        color: #991b1b;
    }

    /* Clean file uploader */
    .uploadedFile {
        border: 1px solid var(--gray-200);
        border-radius: 6px;
    }

    /* Modern card styling */
    .property-card {
        background: var(--bg-light);
        border: 1px solid var(--border-light);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px var(--shadow-light);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px var(--shadow-medium);
        border-color: var(--primary-color);
    }

    .property-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
    }

    .suburb-card {
        background: var(--bg-light);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px var(--shadow-light);
        transition: all 0.3s ease;
    }

    .suburb-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px var(--shadow-medium);
    }

    /* Modern metrics */
    .metric-container {
        background: var(--bg-light);
        border: 1px solid var(--border-light);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px var(--shadow-light);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
    }

    /* Modern grid layouts */
    .modern-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .hero-section {
        background: var(--gradient-hero);
        color: white;
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }

    /* Status indicators */
    .status-complete {
        color: var(--success-color);
        font-weight: 500;
    }

    .status-pending {
        color: var(--gray-400);
        font-weight: 500;
    }

    .status-in-progress {
        color: var(--primary-color);
        font-weight: 500;
    }

    /* Remove default streamlit branding elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Professional table styling */
    .dataframe thead th {
        background-color: var(--gray-50);
        color: var(--gray-700);
        font-weight: 600;
    }

    /* Clean plotly charts */
    .js-plotly-plot .plotly .modebar {
        background: transparent;
    }

    /* Sidebar toggle functionality */
    .sidebar-toggle-btn {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        transition: all 0.2s ease;
        display: none;
    }

    .sidebar-toggle-btn:hover {
        background: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    /* Show toggle button when sidebar is collapsed */
    .stApp[data-sidebar-state="collapsed"] .sidebar-toggle-btn {
        display: block;
    }

    /* Hide default streamlit sidebar toggle when we have our custom one */
    .stApp[data-sidebar-state="collapsed"] .css-1rs6os {
        display: none;
    }

    /* Improve sidebar animation */
    .css-1d391kg {
        transition: all 0.3s ease;
    }

    /* Custom sidebar state detection styles */
    .main-content {
        transition: margin-left 0.3s ease;
    }

    /* When sidebar is collapsed, adjust main content */
    .stApp[data-sidebar-state="collapsed"] .main-content {
        margin-left: 0;
    }

    /* Style the sidebar close button better */
    .css-1rs6os .css-1v0mbdj {
        color: var(--gray-500);
        font-size: 18px;
    }

    .css-1rs6os .css-1v0mbdj:hover {
        color: var(--gray-700);
    }
    </style>

    <script>
    // Sidebar toggle functionality
    function initSidebarToggle() {
        // Create toggle button
        if (!document.getElementById('sidebar-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.id = 'sidebar-toggle';
            toggleBtn.className = 'sidebar-toggle-btn';
            toggleBtn.innerHTML = '☰ Menu';
            toggleBtn.onclick = function() {
                toggleSidebar();
            };
            document.body.appendChild(toggleBtn);
        }

        // Monitor sidebar state
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    updateSidebarState();
                }
            });
        });

        // Observe main app container for class changes
        const appContainer = document.querySelector('.stApp');
        if (appContainer) {
            observer.observe(appContainer, { attributes: true });
            updateSidebarState();
        }
    }

    function updateSidebarState() {
        const sidebar = document.querySelector('.css-1d391kg');
        const appContainer = document.querySelector('.stApp');
        const toggleBtn = document.getElementById('sidebar-toggle');

        if (sidebar && appContainer && toggleBtn) {
            const sidebarRect = sidebar.getBoundingClientRect();
            const isCollapsed = sidebarRect.width < 50;

            if (isCollapsed) {
                appContainer.setAttribute('data-sidebar-state', 'collapsed');
                toggleBtn.style.display = 'block';
                toggleBtn.innerHTML = '☰ Menu';
            } else {
                appContainer.setAttribute('data-sidebar-state', 'expanded');
                toggleBtn.style.display = 'none';
            }
        }
    }

    function toggleSidebar() {
        // Find and click the default Streamlit sidebar toggle
        const toggleButtons = document.querySelectorAll('[data-testid="collapsedControl"]');
        if (toggleButtons.length > 0) {
            toggleButtons[0].click();
        } else {
            // Alternative: trigger resize event to show sidebar
            window.dispatchEvent(new Event('resize'));
        }
    }

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', initSidebarToggle);

    // Also initialize after a delay to ensure Streamlit is fully loaded
    setTimeout(initSidebarToggle, 1000);
    </script>

    <style>
    /* Aggressive whitespace removal */
    .stApp {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove top toolbar padding */
    .stApp > header {
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Compact main content */
    .main > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Remove margins from all major containers */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Compact element spacing */
    .element-container {
        margin: 0.25rem 0 !important;
    }

    /* Remove spacing from dividers */
    hr {
        margin: 0.5rem 0 !important;
    }

    /* Compact sections */
    section {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove gaps from columns */
    .css-1r6slb0 {
        gap: 0.5rem !important;
    }

    /* Compact markdown elements */
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }

    /* Remove excessive spacing from buttons */
    .stButton {
        margin: 0.25rem 0 !important;
    }

    /* Compact forms */
    .stForm {
        padding: 0.5rem !important;
        margin: 0.5rem 0 !important;
    }

    /* Remove whitespace from top of sidebar */
    section[data-testid="stSidebar"] .css-1d391kg {
        padding-top: 0.5rem !important;
    }

    /* Compact expander */
    .streamlit-expanderHeader {
        padding: 0.5rem !important;
    }

    /* Remove gap from tabs */
    .stTabs {
        margin-bottom: 0.5rem !important;
    }

    /* Compact tab content */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove padding from tab panel containers */
    .stTabs [data-baseweb="tab-panel"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Target specific tab content areas */
    .stTabs [data-baseweb="tab-panel"] .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove padding from first elements in tabs */
    .stTabs [data-baseweb="tab-panel"] > div > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* More aggressive tab content targeting */
    .stTabs [data-baseweb="tab-panel"] * {
        margin-top: 0 !important;
    }

    .stTabs [data-baseweb="tab-panel"] > div:first-child {
        padding-top: 0 !important;
    }

    /* Remove top margin from hero sections in tabs */
    .stTabs [data-baseweb="tab-panel"] div[style*="background"] {
        margin-top: 0 !important;
    }

    /* Ensure no top spacing on any elements immediately after tab headers */
    .stTabs [data-baseweb="tab-list"] + div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Nuclear option - remove ALL top spacing */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove all top spacing from root elements */
    #root {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Streamlit app container */
    .stApp {
        margin-top: 0 !important;
        padding-top: 0 !important;
        top: 0 !important;
    }

    /* Main content wrapper */
    .main {
        margin-top: 0 !important;
        padding-top: 0 !important;
        top: 0 !important;
    }

    /* Block container aggressive targeting */
    .main .block-container {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Remove any toolbar/header spacing */
    .stApp > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Target the first element in main content */
    .main > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Remove spacing from first child of block container */
    .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Nuclear approach - all first children */
    *:first-child {
        margin-top: 0 !important;
    }

    /* Remove any default browser spacing */
    * {
        margin-top: 0 !important;
        box-sizing: border-box !important;
    }

    /* Specific targeting for hero sections */
    div[style*="background: linear-gradient"] {
        margin-top: 0 !important;
        padding-top: 2rem !important; /* Keep internal padding but no margin */
    }

    /* More targeted approach - keep functionality */
    .stApp {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Hide toolbar but keep layout */
    div[data-testid="stToolbar"] {
        display: none !important;
    }

    /* Hide status container */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Target streamlit header */
    .stApp > header {
        display: none !important;
    }

    /* Reduce main container spacing */
    .main {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Zero out block container top spacing */
    .main .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Target any invisible spacer elements */
    .stApp > div[style*="height"] {
        height: 0 !important;
        min-height: 0 !important;
    }

    /* Remove ALL sidebar top whitespace */
    section[data-testid="stSidebar"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Sidebar content container */
    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Sidebar inner container */
    section[data-testid="stSidebar"] .css-1d391kg {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* All sidebar child elements */
    section[data-testid="stSidebar"] * {
        margin-top: 0 !important;
    }

    /* First element in sidebar */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Sidebar block container */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Target specific sidebar CSS classes */
    .css-1d391kg,
    .css-1cypcdb,
    .css-17eq0hr {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove padding from sidebar header/logo area */
    section[data-testid="stSidebar"] div[style*="text-align: center"] {
        margin-top: 0 !important;
        padding-top: 1rem !important; /* Keep minimal padding for the logo */
    }

    /* Target progress indicator area */
    section[data-testid="stSidebar"] div[style*="margin-bottom: 1rem"] {
        margin-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)