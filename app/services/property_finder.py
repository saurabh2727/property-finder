import pandas as pd
import numpy as np
import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

class PropertyFinder:
    """
    Step 8: Property Finder - Pull current listings within shortlisted suburbs
    Filter by configuration and run quick cashflow calculations
    """

    def __init__(self):
        self.api_endpoints = {
            'domain': 'https://api.domain.com.au/v1/listings/residential/_search',
            'realestate': 'https://services.realestate.com.au/services/listings/search',
            'mock': 'https://jsonplaceholder.typicode.com/posts'  # Mock API for testing
        }
        self.mock_data_enabled = True  # Enable mock data for MVP

    def find_properties_in_suburbs(self, shortlisted_suburbs: pd.DataFrame, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Find current property listings in shortlisted suburbs"""

        property_results = {}

        for idx, suburb_row in shortlisted_suburbs.iterrows():
            suburb_name = suburb_row.get('Suburb', f'Suburb_{idx}')
            state = suburb_row.get('State', 'NSW')

            st.write(f"🏠 Searching properties in {suburb_name}, {state}...")

            # Get property listings for this suburb
            listings = self._get_listings_for_suburb(suburb_name, state, customer_profile)

            # Filter and process listings
            filtered_listings = self._filter_listings(listings, customer_profile, suburb_row)

            # Add cashflow calculations
            listings_with_cashflow = self._add_cashflow_calculations(filtered_listings, suburb_row)

            # Add risk flags
            listings_with_flags = self._add_risk_flags(listings_with_cashflow, suburb_row)

            property_results[suburb_name] = {
                'suburb_data': suburb_row.to_dict(),
                'total_listings': len(listings),
                'filtered_listings': len(listings_with_flags),
                'properties': listings_with_flags
            }

        return property_results

    def _get_listings_for_suburb(self, suburb: str, state: str, customer_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get property listings for a specific suburb"""

        if self.mock_data_enabled:
            return self._generate_mock_listings(suburb, state, customer_profile)

        # Real API integration (to be implemented with actual API keys)
        try:
            # This would integrate with Domain, REA, or other property APIs
            # For now, return mock data
            return self._generate_mock_listings(suburb, state, customer_profile)

        except Exception as e:
            st.warning(f"Could not fetch real listings for {suburb}. Using mock data.")
            return self._generate_mock_listings(suburb, state, customer_profile)

    def _generate_mock_listings(self, suburb: str, state: str, customer_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate realistic mock property listings for testing"""

        # Get customer preferences
        property_prefs = customer_profile.get('property_preferences', {})
        price_range = property_prefs.get('price_range', {})
        property_types = property_prefs.get('property_types', ['house'])

        try:
            min_price = float(str(price_range.get('min', '500000')).replace('$', '').replace(',', ''))
            max_price = float(str(price_range.get('max', '800000')).replace('$', '').replace(',', ''))
        except:
            min_price, max_price = 500000, 800000

        # Generate 5-15 mock listings
        num_listings = np.random.randint(5, 16)
        listings = []

        for i in range(num_listings):
            # Random property details
            bedrooms = np.random.choice([2, 3, 4, 5], p=[0.1, 0.4, 0.4, 0.1])
            bathrooms = min(bedrooms, np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2]))
            parking = np.random.choice([0, 1, 2, 3], p=[0.1, 0.3, 0.4, 0.2])

            # Price based on bedrooms and customer range
            base_price = np.random.uniform(min_price * 0.8, max_price * 1.2)
            bedroom_multiplier = {2: 0.8, 3: 1.0, 4: 1.3, 5: 1.6}
            estimated_price = base_price * bedroom_multiplier.get(bedrooms, 1.0)

            # Property type
            if property_types:
                property_type = np.random.choice(property_types)
            else:
                property_type = np.random.choice(['house', 'unit', 'townhouse'], p=[0.6, 0.3, 0.1])

            # Address
            street_names = ['Main St', 'Oak Ave', 'Cedar Rd', 'Pine Cres', 'Elm Dr', 'Maple Ln']
            street_number = np.random.randint(1, 200)
            address = f"{street_number} {np.random.choice(street_names)}, {suburb}, {state}"

            # Listing details
            listing = {
                'id': f"{suburb.lower().replace(' ', '_')}_{i+1}",
                'address': address,
                'suburb': suburb,
                'state': state,
                'property_type': property_type.title(),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'parking': parking,
                'estimated_price': int(estimated_price),
                'price_display': f"${estimated_price:,.0f}",
                'land_size': np.random.randint(300, 1000) if property_type == 'house' else None,
                'floor_area': np.random.randint(80, 250),
                'listing_date': datetime.now().strftime('%Y-%m-%d'),
                'days_on_market': np.random.randint(1, 120),
                'description': f"Beautiful {bedrooms} bedroom {property_type} in sought-after {suburb}. Features modern amenities and great location.",
                'agent': f"Agent {np.random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Davis'])}",
                'agency': f"{np.random.choice(['Premium', 'Elite', 'First National', 'Ray White', 'LJ Hooker'])} Real Estate",
                'listing_url': f"https://example.com/listing/{suburb.lower()}_{i+1}"
            }

            listings.append(listing)

        return listings

    def _filter_listings(self, listings: List[Dict[str, Any]], customer_profile: Dict[str, Any], suburb_data: pd.Series) -> List[Dict[str, Any]]:
        """Filter listings based on customer requirements"""

        if not listings:
            return []

        property_prefs = customer_profile.get('property_preferences', {})

        # Price filter
        price_range = property_prefs.get('price_range', {})
        if price_range.get('min') and price_range.get('max'):
            try:
                min_price = float(str(price_range['min']).replace('$', '').replace(',', ''))
                max_price = float(str(price_range['max']).replace('$', '').replace(',', ''))

                # Apply with flexibility (±15%)
                flex_min = min_price * 0.85
                flex_max = max_price * 1.15

                listings = [l for l in listings if flex_min <= l.get('estimated_price', 0) <= flex_max]
            except:
                pass

        # Property type filter
        property_types = property_prefs.get('property_types', [])
        if property_types:
            listings = [l for l in listings if l.get('property_type', '').lower() in [pt.lower() for pt in property_types]]

        # Bedroom filter
        bedroom_range = property_prefs.get('bedroom_range', '')
        if bedroom_range and '-' in bedroom_range:
            try:
                min_br, max_br = map(int, bedroom_range.split('-'))
                listings = [l for l in listings if min_br <= l.get('bedrooms', 0) <= max_br]
            except:
                pass

        return listings

    def _add_cashflow_calculations(self, listings: List[Dict[str, Any]], suburb_data: pd.Series) -> List[Dict[str, Any]]:
        """Add quick cashflow calculations to each property"""

        suburb_yield = suburb_data.get('Rental Yield on Houses', 4.0)
        median_price = suburb_data.get('Median Price', 600000)

        for listing in listings:
            price = listing.get('estimated_price', median_price)

            # Estimate rental based on suburb yield and property size
            bedrooms = listing.get('bedrooms', 3)
            bedroom_multiplier = {1: 0.7, 2: 0.85, 3: 1.0, 4: 1.2, 5: 1.4}

            # Base rental calculation
            annual_rent = price * (suburb_yield / 100) * bedroom_multiplier.get(bedrooms, 1.0)
            weekly_rent = annual_rent / 52

            # Expenses (typical percentages)
            expenses = {
                'property_management': annual_rent * 0.08,  # 8%
                'maintenance_repairs': annual_rent * 0.05,  # 5%
                'insurance': annual_rent * 0.02,  # 2%
                'rates_taxes': price * 0.01,  # 1% of property value
                'vacancy_allowance': annual_rent * 0.02  # 2%
            }

            total_annual_expenses = sum(expenses.values())
            net_annual_rent = annual_rent - total_annual_expenses
            net_weekly_rent = net_annual_rent / 52

            # Financing assumptions (80% LVR, 6% interest)
            loan_amount = price * 0.8
            annual_interest = loan_amount * 0.06
            weekly_interest = annual_interest / 52

            # Net cashflow
            net_weekly_cashflow = net_weekly_rent - weekly_interest

            # Add to listing
            listing.update({
                'estimated_weekly_rent': round(weekly_rent),
                'estimated_annual_rent': round(annual_rent),
                'total_annual_expenses': round(total_annual_expenses),
                'net_annual_rent': round(net_annual_rent),
                'net_weekly_cashflow': round(net_weekly_cashflow),
                'rental_yield': round((annual_rent / price) * 100, 2),
                'net_yield': round((net_annual_rent / price) * 100, 2),
                'expenses_breakdown': {k: round(v) for k, v in expenses.items()}
            })

        return listings

    def _add_risk_flags(self, listings: List[Dict[str, Any]], suburb_data: pd.Series) -> List[Dict[str, Any]]:
        """Add risk flags to properties"""

        # Suburb-level risk indicators
        vacancy_rate = suburb_data.get('Vacancy Rate', 3.0)
        days_on_market = suburb_data.get('Sales Days on Market', 30)
        som_percentage = suburb_data.get('Stock on Market Percentage (SOM%)', 3.0)

        risk_flags = []

        # High vacancy risk
        if vacancy_rate > 5.0:
            risk_flags.append('High Vacancy Area')

        # Slow selling market
        if days_on_market > 45:
            risk_flags.append('Slow Market')

        # High stock levels
        if som_percentage > 5.0:
            risk_flags.append('High Stock Levels')

        for listing in listings:
            property_flags = list(risk_flags)

            # Property-specific flags
            if listing.get('days_on_market', 0) > 60:
                property_flags.append('Long Time on Market')

            # Price vs median comparison
            median_price = suburb_data.get('Median Price', 600000)
            if listing.get('estimated_price', 0) > median_price * 1.5:
                property_flags.append('Above Median Premium')

            # Cashflow flags
            if listing.get('net_weekly_cashflow', 0) < -200:
                property_flags.append('Negative Cashflow')

            listing['risk_flags'] = property_flags

        return listings

    def create_property_summary(self, property_results: Dict[str, Any]) -> pd.DataFrame:
        """Create a summary DataFrame of all found properties"""

        summary_data = []

        for suburb_name, suburb_result in property_results.items():
            properties = suburb_result.get('properties', [])

            for prop in properties:
                summary_data.append({
                    'Suburb': suburb_name,
                    'Address': prop.get('address', ''),
                    'Type': prop.get('property_type', ''),
                    'Bedrooms': prop.get('bedrooms', 0),
                    'Price': prop.get('estimated_price', 0),
                    'Weekly Rent': prop.get('estimated_weekly_rent', 0),
                    'Net Cashflow': prop.get('net_weekly_cashflow', 0),
                    'Rental Yield': prop.get('rental_yield', 0),
                    'Days on Market': prop.get('days_on_market', 0),
                    'Risk Flags': ', '.join(prop.get('risk_flags', [])),
                    'Listing URL': prop.get('listing_url', '')
                })

        return pd.DataFrame(summary_data)

    def get_best_properties(self, property_results: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get the best properties across all suburbs based on multiple criteria"""

        all_properties = []

        for suburb_name, suburb_result in property_results.items():
            properties = suburb_result.get('properties', [])
            for prop in properties:
                prop['suburb_name'] = suburb_name
                all_properties.append(prop)

        if not all_properties:
            return []

        # Score properties
        for prop in all_properties:
            score = 0

            # Positive cashflow bonus
            if prop.get('net_weekly_cashflow', 0) > 0:
                score += 30

            # Good yield bonus
            if prop.get('rental_yield', 0) > 4.5:
                score += 20

            # Few days on market bonus
            if prop.get('days_on_market', 0) < 30:
                score += 15

            # No risk flags bonus
            if not prop.get('risk_flags', []):
                score += 10

            # Reasonable price bonus (not too far above median)
            # This would need suburb median data for proper calculation
            score += 5

            prop['property_score'] = score

        # Sort by score and return top N
        sorted_properties = sorted(all_properties, key=lambda x: x.get('property_score', 0), reverse=True)
        return sorted_properties[:top_n]

    def generate_property_insights(self, property_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about the property search results"""

        insights = {
            'total_suburbs_searched': len(property_results),
            'total_properties_found': 0,
            'average_price': 0,
            'average_yield': 0,
            'positive_cashflow_count': 0,
            'properties_with_risks': 0,
            'best_value_suburbs': [],
            'highest_yield_suburbs': []
        }

        all_prices = []
        all_yields = []
        suburb_metrics = []

        for suburb_name, result in property_results.items():
            properties = result.get('properties', [])
            insights['total_properties_found'] += len(properties)

            if properties:
                suburb_avg_price = np.mean([p.get('estimated_price', 0) for p in properties])
                suburb_avg_yield = np.mean([p.get('rental_yield', 0) for p in properties])
                positive_cf_count = sum(1 for p in properties if p.get('net_weekly_cashflow', 0) > 0)
                risk_count = sum(1 for p in properties if p.get('risk_flags', []))

                insights['positive_cashflow_count'] += positive_cf_count
                insights['properties_with_risks'] += risk_count

                all_prices.extend([p.get('estimated_price', 0) for p in properties])
                all_yields.extend([p.get('rental_yield', 0) for p in properties])

                suburb_metrics.append({
                    'suburb': suburb_name,
                    'avg_price': suburb_avg_price,
                    'avg_yield': suburb_avg_yield,
                    'positive_cf_ratio': positive_cf_count / len(properties) if properties else 0
                })

        # Calculate overall averages
        if all_prices:
            insights['average_price'] = np.mean(all_prices)
        if all_yields:
            insights['average_yield'] = np.mean(all_yields)

        # Identify best suburbs
        if suburb_metrics:
            # Best value (lowest average price)
            insights['best_value_suburbs'] = sorted(suburb_metrics, key=lambda x: x['avg_price'])[:3]

            # Highest yield
            insights['highest_yield_suburbs'] = sorted(suburb_metrics, key=lambda x: x['avg_yield'], reverse=True)[:3]

        return insights