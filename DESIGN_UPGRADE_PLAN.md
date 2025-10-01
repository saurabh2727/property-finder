# Property Finder - Design Upgrade Plan
## Making it Look Like Domain/REA

### Current State Analysis
- ✅ Functional UI with basic styling
- ⚠️ Generic Streamlit appearance
- ⚠️ Limited color palette
- ⚠️ Basic typography
- ⚠️ Minimal imagery/visual hierarchy

### Target: Domain/REA-Level Polish

---

## 1. **Color Palette Upgrade**

### Primary Colors (Real Estate Industry Standard)
```python
# Professional Real Estate Palette
COLORS = {
    # Primary Brand
    'primary_blue': '#002F6C',      # Deep professional blue (like Domain)
    'primary_teal': '#00A0AF',      # Modern teal accent

    # Secondary
    'secondary_red': '#E4002B',     # Real estate red (REA-style)
    'secondary_gold': '#F5A623',    # Premium gold accent

    # Neutrals
    'dark_navy': '#001E3C',         # Headers, text
    'slate_gray': '#4A5568',        # Body text
    'light_gray': '#F7FAFC',        # Backgrounds
    'border_gray': '#E2E8F0',       # Borders, dividers

    # Success/Info
    'success_green': '#38A169',     # Success states
    'info_blue': '#3182CE',         # Info messages
    'warning_orange': '#DD6B20',    # Warnings

    # Gradients
    'gradient_primary': 'linear-gradient(135deg, #002F6C 0%, #00A0AF 100%)',
    'gradient_card': 'linear-gradient(180deg, #FFFFFF 0%, #F7FAFC 100%)',
}
```

---

## 2. **Typography Improvements**

### Font Stack (Domain/REA inspired)
```css
/* Primary Font - Clean, Professional */
font-family: 'Inter', 'Helvetica Neue', 'Arial', sans-serif;

/* Display/Headers - Bold, Modern */
font-family: 'Poppins', 'Montserrat', sans-serif;

/* Numbers/Data - Tabular */
font-family: 'Inter', 'SF Mono', monospace;
```

### Size Scale
- **H1**: 2.5rem (40px) - Page titles
- **H2**: 2rem (32px) - Section headers
- **H3**: 1.5rem (24px) - Card titles
- **Body**: 1rem (16px) - Main text
- **Small**: 0.875rem (14px) - Captions, metadata

---

## 3. **Component Redesigns**

### A. Property Cards (Like Domain Listings)
```
┌─────────────────────────────────────┐
│  [Large Property Image]              │
│  ┌──────────────────────────────┐   │
│  │ $850,000                     │   │ ← Price badge overlay
│  └──────────────────────────────┘   │
├─────────────────────────────────────┤
│  📍 Parramatta, NSW                  │
│  🏠 3 bed • 2 bath • 1 car          │
│  ──────────────────────────────────  │
│  Investment Score: ████████░░ 8.5   │
│  💰 Yield: 4.5% | 📈 Growth: 6.2%   │
│                                      │
│  [View Details →]  [Save ♡]         │
└─────────────────────────────────────┘
```

### B. Data Visualization Style
- Clean, minimal charts (like REA market insights)
- Soft shadows, rounded corners
- Interactive tooltips
- Color-coded metrics with legends

### C. Navigation
```
┌────────────────────────────────────────┐
│  Property Insight        🔍 Search     │
│  ─────────────────────────────────────  │
│  Dashboard | Analysis | Properties     │
└────────────────────────────────────────┘
```

---

## 4. **Visual Enhancements**

### A. **Add Property Images**
- Use placeholder images from Unsplash API
- Hero images for each recommended suburb
- Icons for amenities (schools, transport, shops)

### B. **Micro-interactions**
- Hover effects on cards (lift + shadow)
- Smooth transitions (0.2s ease)
- Loading skeleton screens
- Progress indicators with animations

### C. **Spacing & Layout**
```
Container max-width: 1200px
Grid system: 12 columns
Padding: 1.5rem (24px)
Card spacing: 1rem (16px)
Border radius: 8px (cards), 4px (buttons)
```

---

## 5. **Page-Specific Improvements**

### **Dashboard/Home Page**
```
┌─────────────────────────────────────────────┐
│  🏡 Find Your Perfect Investment Property   │
│  [Large hero image with overlay text]       │
│  ──────────────────────────────────────────  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Profile  │ │ Analysis │ │ Report   │    │
│  │   ⬇️     │ │   📊     │ │   📄     │    │
│  └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────┘
```

### **Recommendations Page**
- Map view with suburb markers (like Domain)
- Filter sidebar (sticky)
- Sort options (price, yield, score)
- Comparison mode (side-by-side)

### **Reports**
- Executive summary at top
- Data visualizations (charts, graphs)
- Print-optimized layout
- Professional header/footer

---

## 6. **Streamlit Custom Theme**

### config.toml Update
```toml
[theme]
primaryColor = "#002F6C"        # Deep blue
backgroundColor = "#FFFFFF"     # White
secondaryBackgroundColor = "#F7FAFC"  # Light gray
textColor = "#001E3C"          # Dark navy
font = "sans serif"
```

---

## 7. **Custom CSS Injection**

### Global Styles
```css
/* Card Style - Domain/REA inspired */
.property-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    overflow: hidden;
}

.property-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* Button Styles */
.primary-button {
    background: linear-gradient(135deg, #002F6C 0%, #00A0AF 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.1s;
}

.primary-button:hover {
    transform: scale(1.02);
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(180deg, #FFFFFF 0%, #F7FAFC 100%);
    border-left: 4px solid #00A0AF;
    padding: 1.5rem;
    border-radius: 8px;
}

/* Typography */
h1, h2, h3 {
    color: #001E3C;
    font-weight: 600;
    letter-spacing: -0.02em;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-success {
    background: #D4F4DD;
    color: #22543D;
}

.badge-warning {
    background: #FFF5E5;
    color: #7C2D12;
}
```

---

## 8. **Image Assets Needed**

### Essential Images
1. **Hero Images**
   - Dashboard hero (property/skyline)
   - Section headers

2. **Icons** (SVG, consistent style)
   - Property types (house, apartment, townhouse)
   - Amenities (schools, transport, shops, parks)
   - Features (bed, bath, car, land)

3. **Placeholder Properties**
   - Suburb imagery from Unsplash API
   - Or use colored gradients as fallback

### Where to Source
```python
# Unsplash API (free)
f"https://source.unsplash.com/800x600/?{suburb_name},australia,property"

# Or use Pexels API
# Or fallback to gradient backgrounds
```

---

## 9. **Implementation Priority**

### Phase 1: Quick Wins (1-2 hours)
- [ ] Update color palette in config.toml
- [ ] Add custom CSS for cards and buttons
- [ ] Improve typography (font sizes, weights)
- [ ] Add subtle shadows and borders

### Phase 2: Component Redesign (3-4 hours)
- [ ] Redesign property cards with images
- [ ] Update navigation header
- [ ] Improve data visualizations
- [ ] Add hover effects and transitions

### Phase 3: Advanced Features (5-6 hours)
- [ ] Add map visualization (Folium/Plotly)
- [ ] Implement image loading (Unsplash)
- [ ] Create comparison view
- [ ] Add filter sidebar

### Phase 4: Polish (2-3 hours)
- [ ] Loading states and skeletons
- [ ] Empty states with illustrations
- [ ] Error states with helpful messages
- [ ] Responsive design tweaks

---

## 10. **Code Examples**

### Modern Card Component
```python
def render_property_card(suburb_data):
    st.markdown(f"""
    <div class="property-card">
        <img src="https://source.unsplash.com/800x400/?{suburb_data['name']},australia"
             style="width: 100%; height: 200px; object-fit: cover;">
        <div style="padding: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #001E3C;">{suburb_data['name']}</h3>
                <span class="badge badge-success">Top Pick</span>
            </div>
            <div style="color: #4A5568; margin-bottom: 1rem;">
                📍 {suburb_data['state']} • {suburb_data['distance']}km to CBD
            </div>
            <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <div style="color: #718096; font-size: 0.875rem;">Median Price</div>
                    <div style="color: #001E3C; font-weight: 600; font-size: 1.25rem;">
                        ${suburb_data['price']:,.0f}
                    </div>
                </div>
                <div>
                    <div style="color: #718096; font-size: 0.875rem;">Rental Yield</div>
                    <div style="color: #38A169; font-weight: 600; font-size: 1.25rem;">
                        {suburb_data['yield']:.1f}%
                    </div>
                </div>
            </div>
            <button class="primary-button" style="width: 100%;">
                View Details →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
```

---

## 11. **Inspiration Sources**

### Real Estate Sites to Study
1. **Domain.com.au**
   - Clean card layouts
   - Professional color scheme
   - Excellent data visualization

2. **REA (realestate.com.au)**
   - Sticky filters
   - Map integration
   - Comparison tools

3. **Zillow.com**
   - Interactive charts
   - Neighborhood insights
   - Photo galleries

4. **Rightmove.co.uk**
   - Search experience
   - Property details layout
   - Agent contact design

---

## 12. **Tools & Resources**

### Design Tools
- **Figma** - Create mockups before coding
- **Coolors.co** - Color palette generator
- **Google Fonts** - Typography
- **Heroicons** - Free icon set
- **Unsplash** - Free images

### Streamlit Extensions
```bash
pip install streamlit-extras  # Additional components
pip install streamlit-folium  # Maps
pip install plotly           # Interactive charts
pip install streamlit-card   # Card components
```

---

## Next Steps

Would you like me to:
1. **Implement Phase 1** (Quick wins - colors, CSS)?
2. **Create a new theme file** with Domain/REA colors?
3. **Redesign a specific page** (e.g., recommendations)?
4. **Build reusable card components**?

Let me know which aspect you'd like to tackle first!
