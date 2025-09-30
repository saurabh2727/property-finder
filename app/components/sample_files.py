import streamlit as st
import pandas as pd
from pathlib import Path

def render_sample_files_section():
    """Render a section with downloadable sample files"""

    st.markdown("### 📥 Sample Files")
    st.info("Download these sample files to test the application")

    # Define sample files
    base_path = Path(__file__).parent.parent.parent / "data" / "sample"

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📄 Customer Profile Sample**")
        st.caption("Sample customer requirements document")

        # Load customer profile sample
        customer_file = base_path / "sample_customer_profile.txt"
        if customer_file.exists():
            with open(customer_file, 'r') as f:
                customer_content = f.read()

            st.download_button(
                label="⬇️ Download Customer Profile",
                data=customer_content,
                file_name="sample_customer_profile.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.warning("Customer profile sample not found")

    with col2:
        st.markdown("**📊 Suburb Data Sample**")
        st.caption("Sample property market data CSV")

        # Load suburb data sample
        suburb_file = base_path / "sample_suburb_data.csv"
        if suburb_file.exists():
            df = pd.read_csv(suburb_file)

            st.download_button(
                label="⬇️ Download Suburb Data",
                data=df.to_csv(index=False),
                file_name="sample_suburb_data.csv",
                mime="text/csv",
                use_container_width=True
            )

            # Show preview
            with st.expander("👁️ Preview Data"):
                st.dataframe(df.head(5), use_container_width=True)
        else:
            st.warning("Suburb data sample not found")

    st.markdown("---")

def get_sample_customer_profile():
    """Return sample customer profile content"""
    return """CUSTOMER DISCOVERY QUESTIONNAIRE - PROPERTY INVESTMENT

Client Name: John & Sarah Smith
Date: September 2025
Property Agent: Sample Agent

FINANCIAL PROFILE:
- Combined Annual Income: $180,000
- Available Equity: $150,000 (from current property)
- Estimated Loan Capacity: $600,000
- Current Debt: $350,000 (existing mortgage)
- Cash Available for Deposit: $80,000

INVESTMENT GOALS:
- Primary Purpose: Seeking both capital growth and rental income
- Investment Timeline: Long-term (10+ years)
- Target Rental Yield: Minimum 4.5%
- Expected Growth: 6-8% per annum
- Risk Tolerance: Medium - willing to take calculated risks

PROPERTY PREFERENCES:
- Preferred Areas: Inner suburbs of Sydney or Melbourne
- Property Type: Houses or townhouses (prefer houses)
- Bedrooms: 3-4 bedrooms
- Budget Range: $700,000 - $900,000
- Special Requirements: Near good schools, public transport access

LIFESTYLE FACTORS:
- Proximity to CBD: Medium importance (prefer within 15km)
- School Quality: High importance (planning for family)
- Transport Access: High importance (need train/bus nearby)
- Shopping & Amenities: Medium importance
- Future Development: Interested in established areas with some development potential

EXPERIENCE LEVEL:
- First-time property investors
- Currently own one property (principal residence)
- Have been researching investment properties for 6 months

BUYING READINESS:
- Ready to purchase within 3-6 months
- Pre-approved for loan
- Actively viewing properties

ADDITIONAL NOTES:
- Prefer properties with low maintenance
- Interest in properties that could benefit from minor renovations
- Want properties in areas with strong rental demand
- Open to both Sydney and Melbourne markets
- Looking for suburbs with good growth potential based on infrastructure projects"""

def get_sample_suburb_data():
    """Return sample suburb data as DataFrame"""
    data = {
        'Suburb Name': ['Bondi', 'Parramatta', 'Richmond', 'Southbank', 'Fremantle', 'Glenelg', 'Newtown', 'Carlton', 'Manly', 'Fitzroy'],
        'State': ['NSW', 'NSW', 'VIC', 'VIC', 'WA', 'SA', 'NSW', 'VIC', 'NSW', 'VIC'],
        'Median House Price': [1200000, 850000, 750000, 650000, 580000, 720000, 950000, 780000, 1450000, 820000],
        'Rental Yield Houses': [3.2, 4.5, 4.8, 4.1, 5.2, 4.3, 3.8, 4.4, 2.9, 4.2],
        'Distance to CBD (km)': [8, 25, 12, 2, 19, 11, 6, 3, 17, 4],
        'Total Population': [12500, 25000, 18000, 15000, 28000, 16500, 22000, 14000, 17500, 21000],
        'Vacancy Rate': [2.1, 3.2, 2.8, 3.5, 2.0, 2.9, 2.4, 3.1, 1.8, 2.7],
        'Days on Market': [35, 28, 42, 38, 25, 33, 31, 29, 42, 33],
        '10 Year Growth Rate': [6.2, 5.8, 7.1, 8.2, 4.9, 5.5, 6.8, 7.5, 5.4, 7.3],
        'School Rating': [8.5, 7.8, 7.2, 6.5, 7.9, 8.1, 8.8, 9.2, 9.5, 8.4],
        'Crime Rate': ['Low', 'Medium', 'Low', 'Medium', 'Low', 'Low', 'Medium', 'Medium', 'Low', 'Medium'],
        'Public Transport Score': [9, 10, 7, 10, 8, 7, 9, 10, 8, 9]
    }
    return pd.DataFrame(data)