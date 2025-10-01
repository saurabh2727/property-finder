import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Dict, Any
import re

class HtAGProcessor:
    """
    HtAG Data Processor
    Automatically converts raw HtAG export files into standardized format
    """

    def __init__(self):
        self.required_columns = [
            'Suburb', 'State', 'Median Price', 'Rental Yield on Houses',
            'Distance (km) to CBD', 'Population'
        ]

    def detect_htag_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect if uploaded file is HtAG format and identify column mappings"""

        detection_result = {
            'is_htag': False,
            'format_type': 'unknown',
            'column_mappings': {},
            'confidence': 0.0,
            'issues': []
        }

        if df is None or df.empty:
            detection_result['issues'].append("Empty dataframe")
            return detection_result

        columns = [col.lower().strip() for col in df.columns]

        # HtAG column patterns to look for (enhanced for real HtAG files)
        htag_patterns = {
            'suburb': [
                'suburb', 'suburb name', 'location', 'area',
                'suburb_name', 'suburb-name'
            ],
            'state': [
                'state', 'st', 'province', 'region'
            ],
            'median_price': [
                'median price', 'median_price', 'price', 'median house price',
                'house price', 'property price', 'median property price',
                'median sale price', 'median value'
            ],
            'rental_yield': [
                'rental yield', 'yield', 'gross yield', 'rental yield on houses',
                'house yield', 'rental_yield', 'gross_yield', 'yield %',
                'rental return', 'yield houses'
            ],
            'distance_cbd': [
                'distance to cbd', 'distance (km) to cbd', 'distance_to_cbd',
                'cbd distance', 'distance from cbd', 'km to cbd',
                'distance to city', 'city distance', 'nearest gpo'
            ],
            'population': [
                'population', 'total population', 'residents', 'pop',
                'population count', 'area population'
            ]
        }

        # Try to match columns
        matched_columns = {}
        confidence_score = 0

        for standard_name, patterns in htag_patterns.items():
            best_match = None
            best_score = 0

            for col in columns:
                for pattern in patterns:
                    # Exact match
                    if col == pattern:
                        best_match = col
                        best_score = 1.0
                        break
                    # Partial match
                    elif pattern in col or col in pattern:
                        score = len(pattern) / max(len(col), len(pattern))
                        if score > best_score and score > 0.6:
                            best_match = col
                            best_score = score

            if best_match and best_score > 0.6:
                # Find original column name (with proper case)
                original_col = None
                for orig_col in df.columns:
                    if orig_col.lower().strip() == best_match:
                        original_col = orig_col
                        break

                if original_col:
                    matched_columns[standard_name] = original_col
                    confidence_score += best_score

        # Calculate overall confidence
        total_required = len(htag_patterns)
        detection_result['confidence'] = confidence_score / total_required

        # Determine if this is likely HtAG format
        if len(matched_columns) >= 4 and detection_result['confidence'] > 0.6:
            detection_result['is_htag'] = True
            detection_result['format_type'] = 'htag'
            detection_result['column_mappings'] = matched_columns

            # Check for missing required columns
            missing_cols = []
            for req_col in ['suburb', 'state', 'median_price']:
                if req_col not in matched_columns:
                    missing_cols.append(req_col)

            if missing_cols:
                detection_result['issues'].append(f"Missing required columns: {missing_cols}")
        else:
            detection_result['issues'].append("Could not reliably identify HtAG format")

        return detection_result

    def process_htag_data(self, df: pd.DataFrame, detection_result: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Process raw HtAG data into standardized format"""

        if not detection_result['is_htag']:
            st.error("File is not recognized as HtAG format")
            return None

        try:
            st.info("🔄 Processing HtAG data...")

            processed_df = df.copy()
            column_mappings = detection_result['column_mappings']

            # Step 1: Rename columns to standard names
            rename_mapping = {}
            for standard_name, original_col in column_mappings.items():
                if standard_name == 'suburb':
                    rename_mapping[original_col] = 'Suburb'
                elif standard_name == 'state':
                    rename_mapping[original_col] = 'State'
                elif standard_name == 'median_price':
                    rename_mapping[original_col] = 'Median Price'
                elif standard_name == 'rental_yield':
                    rename_mapping[original_col] = 'Rental Yield on Houses'
                elif standard_name == 'distance_cbd':
                    rename_mapping[original_col] = 'Distance (km) to CBD'
                elif standard_name == 'population':
                    rename_mapping[original_col] = 'Population'

            processed_df = processed_df.rename(columns=rename_mapping)
            st.success(f"✅ Renamed {len(rename_mapping)} columns")

            # Step 2: Clean and standardize data
            processed_df = self._clean_htag_data(processed_df)

            # Step 3: Add any missing standard columns with defaults
            processed_df = self._add_missing_columns(processed_df)

            # Step 4: Validate processed data
            validation_result = self._validate_processed_data(processed_df)

            if validation_result['is_valid']:
                st.success(f"✅ HtAG data processed successfully: {len(processed_df)} suburbs")
                return processed_df
            else:
                st.warning("⚠️ Data processed with some issues:")
                for issue in validation_result['issues']:
                    st.write(f"  • {issue}")
                return processed_df

        except Exception as e:
            st.error(f"❌ Error processing HtAG data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return None

    def _clean_htag_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize HtAG data"""

        cleaned_df = df.copy()

        # Clean suburb names
        if 'Suburb' in cleaned_df.columns:
            cleaned_df['Suburb'] = cleaned_df['Suburb'].astype(str).str.strip().str.title()
            cleaned_df['Suburb'] = cleaned_df['Suburb'].replace(['Nan', 'None', ''], np.nan)

        # Clean state names
        if 'State' in cleaned_df.columns:
            cleaned_df['State'] = cleaned_df['State'].astype(str).str.strip().str.upper()
            # Standardize state abbreviations
            state_mapping = {
                'NEW SOUTH WALES': 'NSW',
                'VICTORIA': 'VIC',
                'QUEENSLAND': 'QLD',
                'SOUTH AUSTRALIA': 'SA',
                'WESTERN AUSTRALIA': 'WA',
                'TASMANIA': 'TAS',
                'NORTHERN TERRITORY': 'NT',
                'AUSTRALIAN CAPITAL TERRITORY': 'ACT'
            }
            cleaned_df['State'] = cleaned_df['State'].replace(state_mapping)

        # Clean numeric columns (including percentage columns)
        numeric_columns = [
            'Median Price', 'Rental Yield on Houses', 'Distance (km) to CBD', 'Population',
            'Vacancy Rate', 'Days on Market', '10 Year Growth Rate', 'Sales Days on Market',
            '10 yr Avg. Annual Growth'
        ]

        for col in numeric_columns:
            if col in cleaned_df.columns:
                # Remove currency symbols, commas, and percentage signs
                if cleaned_df[col].dtype == 'object':
                    cleaned_df[col] = cleaned_df[col].astype(str)
                    cleaned_df[col] = cleaned_df[col].str.replace('$', '', regex=False)
                    cleaned_df[col] = cleaned_df[col].str.replace(',', '', regex=False)
                    cleaned_df[col] = cleaned_df[col].str.replace('%', '', regex=False)
                    cleaned_df[col] = cleaned_df[col].str.replace(' ', '', regex=False)

                    # Handle ranges (take average)
                    cleaned_df[col] = cleaned_df[col].apply(self._handle_range_values)

                # Convert to numeric
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

        # Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how='all')

        # Remove rows where suburb is missing
        if 'Suburb' in cleaned_df.columns:
            cleaned_df = cleaned_df.dropna(subset=['Suburb'])

        return cleaned_df

    def _handle_range_values(self, value):
        """Handle range values like '500,000 - 600,000' by taking the average"""

        if pd.isna(value) or value in ['', 'nan', 'None']:
            return np.nan

        value_str = str(value).strip()

        # Check for range patterns
        if '-' in value_str:
            parts = value_str.split('-')
            if len(parts) == 2:
                try:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return (min_val + max_val) / 2
                except:
                    pass

        # Check for 'to' patterns
        if ' to ' in value_str.lower():
            parts = value_str.lower().split(' to ')
            if len(parts) == 2:
                try:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return (min_val + max_val) / 2
                except:
                    pass

        return value

    def _add_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add missing standard columns with appropriate defaults"""

        standard_columns = {
            'Suburb': 'Unknown',
            'State': 'NSW',
            'Median Price': 500000,
            'Rental Yield on Houses': 4.0,
            'Distance (km) to CBD': 25,
            'Population': 15000,
            'Region': 'Unknown',
            'Vacancy Rate': 3.0,
            'Sales Days on Market': 35,
            '10 yr Avg. Annual Growth': 5.0
        }

        for col, default_value in standard_columns.items():
            if col not in df.columns:
                df[col] = default_value

        return df

    def _validate_processed_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the processed data quality"""

        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': []
        }

        # Check for required columns
        required_cols = ['Suburb', 'State', 'Median Price']
        missing_required = [col for col in required_cols if col not in df.columns]

        if missing_required:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Missing required columns: {missing_required}")

        # Check data quality
        if len(df) == 0:
            validation_result['is_valid'] = False
            validation_result['issues'].append("No data rows remaining after processing")

        # Check for reasonable value ranges
        if 'Median Price' in df.columns:
            price_issues = []
            if df['Median Price'].min() < 50000:
                price_issues.append("Very low median prices detected")
            if df['Median Price'].max() > 10000000:
                price_issues.append("Very high median prices detected")
            if df['Median Price'].isnull().sum() > len(df) * 0.5:
                price_issues.append("More than 50% of price data is missing")

            validation_result['warnings'].extend(price_issues)

        if 'Rental Yield on Houses' in df.columns:
            yield_col = df['Rental Yield on Houses']
            if yield_col.min() < 0:
                validation_result['warnings'].append("Negative rental yields detected")
            if yield_col.max() > 20:
                validation_result['warnings'].append("Very high rental yields detected (>20%)")

        return validation_result

    def create_sample_htag_data(self) -> pd.DataFrame:
        """Create sample HtAG-format data for testing"""

        sample_data = pd.DataFrame({
            'Suburb Name': ['Bondi', 'Parramatta', 'Richmond', 'Southbank', 'Fremantle', 'Glenelg'],
            'State': ['NSW', 'NSW', 'VIC', 'VIC', 'WA', 'SA'],
            'Median House Price': ['$1,200,000', '$850,000', '$750,000', '$650,000', '$580,000', '$720,000'],
            'Rental Yield Houses': ['3.2%', '4.5%', '4.8%', '4.1%', '5.2%', '4.3%'],
            'Distance to CBD (km)': [8, 25, 12, 2, 19, 11],
            'Total Population': ['12,500', '25,000', '18,000', '15,000', '28,000', '16,500'],
            'Vacancy Rate': [2.1, 3.2, 2.8, 3.5, 2.0, 2.9],
            'Days on Market': [35, 28, 42, 38, 25, 33],
            '10 Year Growth Rate': ['6.2%', '5.8%', '7.1%', '8.2%', '4.9%', '5.5%']
        })

        return sample_data

    def export_processed_data(self, df: pd.DataFrame, output_path: str = None) -> str:
        """Export processed data to CSV"""

        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"htag_processed_{timestamp}.csv"

        try:
            df.to_csv(output_path, index=False)
            return output_path
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return None