#!/usr/bin/env python3
"""
Convert HtAG Analytics Excel file to Property Finder compatible format
"""
import pandas as pd
import numpy as np
import re
import sys

def convert_htag_data(input_file, output_file=None):
    """Convert HtAG Analytics data to Property Finder format"""

    try:
        print("🔄 Reading HtAG Analytics file...")

        # Read with correct header row (row 2, 0-indexed)
        df = pd.read_excel(input_file, header=2)

        print(f"✅ Loaded {len(df)} rows with {len(df.columns)} columns")

        # Debug: show actual column names
        print("🔍 Available columns:")
        for i, col in enumerate(df.columns[:20]):  # Show first 20 columns
            print(f"  {i+1:2d}. {col}")
        if len(df.columns) > 20:
            print(f"     ... and {len(df.columns) - 20} more")

        # Find the area/suburb column (it might not be exactly 'Area')
        area_column = None
        for col in df.columns:
            if 'area' in col.lower() or col.strip().lower() == 'area':
                area_column = col
                break

        # If no 'Area' column found, check the first column
        if area_column is None and len(df.columns) > 0:
            # Check if first column contains suburb-like data
            first_col = df.columns[0]
            sample_value = str(df[first_col].iloc[0]) if not df[first_col].empty else ""
            if ',' in sample_value and any(state in sample_value.upper() for state in ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']):
                area_column = first_col
                print(f"📍 Using '{first_col}' as suburb column")

        if area_column is None:
            raise ValueError("Could not find suburb/area column in the data")

        print(f"🏘️  Processing suburb and state data from column: '{area_column}'")

        # Extract suburb and state from area column
        # Area format is typically: "Suburb Name, STATE postcode"
        df['Suburb_Clean'] = df[area_column].str.extract(r'^([^,]+)')
        df['State_Clean'] = df[area_column].str.extract(r',\s*(\w{2,3})\s+\d+')

        # Handle cases where state might not be extracted properly
        df['State_Clean'] = df['State_Clean'].fillna(df['State'] if 'State' in df.columns else 'NSW')

        # Create the converted dataframe with required columns
        converted_df = pd.DataFrame()

        # Map columns according to Property Finder requirements
        print("🗺️  Mapping columns...")

        converted_df['Suburb'] = df['Suburb_Clean'].str.strip()
        converted_df['State'] = df['State_Clean'].str.strip().str.upper()
        converted_df['Region'] = df['SA4'] if 'SA4' in df.columns else 'Unknown'

        # Price data
        converted_df['Median Price'] = pd.to_numeric(df['Price'], errors='coerce')

        # Rental yield (convert from decimal to percentage)
        yield_values = pd.to_numeric(df['Yield'], errors='coerce')
        # If values are in decimal format (0.04 = 4%), convert to percentage
        if yield_values.max() < 1:
            yield_values = yield_values * 100
        converted_df['Rental Yield on Houses'] = yield_values

        # Distance to CBD - try to find appropriate column
        if 'Nearest GPO' in df.columns:
            converted_df['Distance (km) to CBD'] = pd.to_numeric(df['Nearest GPO'], errors='coerce')
        else:
            # Estimate based on region or set default
            converted_df['Distance (km) to CBD'] = 25  # Default estimate

        # Population
        converted_df['Population'] = pd.to_numeric(df['Population'], errors='coerce')

        # Additional useful columns if available
        if 'Vacancy Rate' in df.columns:
            converted_df['Vacancy Rate'] = pd.to_numeric(df['Vacancy Rate'], errors='coerce')

        if 'DoM' in df.columns:
            converted_df['Sales Days on Market'] = pd.to_numeric(df['DoM'], errors='coerce')

        # Growth rate - try multiple possible column names in order of preference
        growth_rate_found = False

        # Try PΔ10Y first (10-year price delta) - convert from decimal to percentage
        if 'PΔ10Y' in df.columns:
            growth_values = pd.to_numeric(df['PΔ10Y'], errors='coerce')
            # Convert from cumulative 10-year growth to annual rate
            # Formula: annual_rate = (1 + total_growth)^(1/10) - 1
            annual_growth = ((1 + growth_values) ** (1/10) - 1) * 100
            converted_df['10 yr Avg. Annual Growth'] = annual_growth
            growth_rate_found = True
            print(f"✅ Using 'PΔ10Y' for growth rate (converted to annual %)")

        # Try Capital Growth as a score/index
        elif 'Capital Growth' in df.columns:
            cg_values = pd.to_numeric(df['Capital Growth'], errors='coerce')
            # Assume Capital Growth is a score out of 100, convert to estimated annual %
            # Higher scores suggest better growth potential
            estimated_growth = 2.0 + (cg_values / 100) * 6.0  # Range: 2-8% based on score
            converted_df['10 yr Avg. Annual Growth'] = estimated_growth
            growth_rate_found = True
            print(f"✅ Using 'Capital Growth' score for growth rate estimation")

        # Try other growth-related columns
        else:
            for col_name in ['GRC Index', 'PΔ5Y', 'PΔ3Y']:
                if col_name in df.columns:
                    if 'PΔ' in col_name:
                        # Extract years from column name and convert appropriately
                        years = int(col_name.replace('PΔ', '').replace('Y', ''))
                        growth_values = pd.to_numeric(df[col_name], errors='coerce')
                        annual_growth = ((1 + growth_values) ** (1/years) - 1) * 100
                        converted_df['10 yr Avg. Annual Growth'] = annual_growth
                    else:
                        converted_df['10 yr Avg. Annual Growth'] = pd.to_numeric(df[col_name], errors='coerce')
                    growth_rate_found = True
                    print(f"✅ Using '{col_name}' for growth rate")
                    break

        # If no growth rate column found, estimate based on price and yield
        if not growth_rate_found:
            print("⚠️  No growth rate column found, estimating...")
            # Estimate growth based on yield and market characteristics
            if 'Rental Yield on Houses' in converted_df.columns:
                # Higher yield often correlates with higher growth potential in regional areas
                base_growth = 4.0  # Base growth rate
                yield_bonus = (converted_df['Rental Yield on Houses'] - 3.0) * 0.5
                converted_df['10 yr Avg. Annual Growth'] = np.maximum(2.0, base_growth + yield_bonus)
            else:
                converted_df['10 yr Avg. Annual Growth'] = 5.0  # Default estimate

        # Clean the data
        print("🧹 Cleaning data...")

        # Remove rows with missing critical data
        critical_columns = ['Suburb', 'State', 'Median Price']
        converted_df = converted_df.dropna(subset=critical_columns)

        # Remove duplicates
        converted_df = converted_df.drop_duplicates(subset=['Suburb', 'State'])

        # Filter out rows with unrealistic data
        converted_df = converted_df[
            (converted_df['Median Price'] >= 100000) &
            (converted_df['Median Price'] <= 10000000)
        ]

        if 'Rental Yield on Houses' in converted_df.columns:
            converted_df = converted_df[
                (converted_df['Rental Yield on Houses'] >= 0) &
                (converted_df['Rental Yield on Houses'] <= 20)
            ]

        print(f"✅ Cleaned data: {len(converted_df)} valid suburbs")

        # Show sample of converted data
        print("\n📊 SAMPLE CONVERTED DATA:")
        print(converted_df.head().to_string())

        print(f"\n📈 DATA SUMMARY:")
        print(f"Suburbs: {len(converted_df)}")
        print(f"States: {converted_df['State'].unique()}")
        print(f"Price range: ${converted_df['Median Price'].min():,.0f} - ${converted_df['Median Price'].max():,.0f}")
        if 'Rental Yield on Houses' in converted_df.columns:
            print(f"Yield range: {converted_df['Rental Yield on Houses'].min():.1f}% - {converted_df['Rental Yield on Houses'].max():.1f}%")

        # Save converted file
        if output_file is None:
            output_file = input_file.replace('.xlsx', '_converted.csv')

        converted_df.to_csv(output_file, index=False)
        print(f"\n💾 Saved converted data to: {output_file}")

        return converted_df, output_file

    except Exception as e:
        print(f"❌ Error converting data: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    input_file = "/Users/saurabh.v.mishra/Desktop/My-Projects/property-finder/data/raw/Main Dashboard - HtAG Analytics (2).xlsx"
    output_file = "/Users/saurabh.v.mishra/Desktop/My-Projects/property-finder/data/processed/htag_converted.csv"

    print("🏠 HtAG Analytics Data Converter")
    print("=" * 50)

    df, output_path = convert_htag_data(input_file, output_file)

    if df is not None:
        print("=" * 50)
        print("🎉 Conversion completed successfully!")
        print(f"📂 Use this file in the Property Finder app: {output_path}")
    else:
        print("=" * 50)
        print("❌ Conversion failed. Please check the error messages above.")