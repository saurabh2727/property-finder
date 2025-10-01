# Sample Files Guide

## 📥 How Sample Files Work in Streamlit Cloud

### Problem Solved
In localhost, you could access files from local directories. But in Streamlit Cloud, users don't have access to your local file system.

### Solution Implemented
We've created **downloadable sample files** that are:
1. ✅ Stored in the repository (`data/sample/` directory)
2. ✅ Deployed with your app to Streamlit Cloud
3. ✅ Available for download directly in the app

## 📂 Sample Files Included

### 1. Customer Profile Sample (`sample_customer_profile.txt`)
- **Location:** `data/sample/sample_customer_profile.txt`
- **Purpose:** Example customer discovery questionnaire
- **Content:** Complete profile for "John & Sarah Smith" including:
  - Financial profile ($180k income, $150k equity)
  - Investment goals (long-term, 4.5% yield target)
  - Property preferences (3-4 bed houses, $700k-$900k)
  - Lifestyle factors (schools, transport)

### 2. Suburb Data Sample (`sample_suburb_data.csv`)
- **Location:** `data/sample/sample_suburb_data.csv`
- **Purpose:** Example property market data
- **Content:** 20 Australian suburbs with metrics:
  - Median prices, rental yields
  - Distance to CBD, population
  - Vacancy rates, growth rates
  - School ratings, crime rates
  - Public transport scores

## 🎯 Where Users Can Access Sample Files

### 1. **Home Page (Dashboard)**
- Prominent sample files section with download buttons
- Shows data preview for suburb data
- Available immediately when app loads

### 2. **Customer Profile Page**
- Collapsible "Need a sample file?" expander
- Right before the file upload section
- Easy access when users need it

### 3. **Data Upload Page**
- Sample files section at the top
- Visible before data source information
- Helps users understand expected format

## 💡 How Users Use Sample Files

1. **User clicks download button** → File downloads to their computer
2. **User goes to upload section** → Clicks "Upload file"
3. **User selects downloaded file** → App processes it normally

## 🔧 Technical Implementation

### Component: `app/components/sample_files.py`
```python
def render_sample_files_section():
    # Reads files from data/sample/
    # Creates download buttons
    # Shows data preview
```

### File Structure:
```
property-finder/
├── data/
│   └── sample/
│       ├── sample_customer_profile.txt
│       ├── sample_suburb_data.csv
│       └── sample_htag_data.csv (legacy)
└── app/
    └── components/
        └── sample_files.py
```

### .gitignore Configuration:
```gitignore
data/*              # Ignore all data files
!data/sample/       # EXCEPT sample directory
!data/sample/*      # Include all files in sample
```

## ✅ Benefits

1. **No Local File Dependency**: Works on any deployment platform
2. **User-Friendly**: One-click download
3. **Always Available**: Files deploy with the app
4. **Version Controlled**: Sample files in git repository
5. **Format Reference**: Users see expected data structure

## 🚀 For Streamlit Cloud

When you deploy to Streamlit Cloud:
- ✅ Sample files automatically included
- ✅ Download buttons work immediately
- ✅ No additional configuration needed
- ✅ Users can test full workflow without their own data

## 📝 Adding More Sample Files

To add new sample files:

1. Create file in `data/sample/` directory
2. Update `sample_files.py` to include new file
3. Add download button in component
4. Commit and push to GitHub
5. Streamlit Cloud auto-deploys

## 🎉 Result

Users can now fully test your app on Streamlit Cloud without needing:
- Local files
- File sharing services
- Email attachments
- External links

Everything is self-contained and ready to use! 🚀