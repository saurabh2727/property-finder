"""
Column Schema Registry
======================
Single source of truth for all column names in the data pipeline.

Every column the app uses is defined here with:
- canonical_name: the name used throughout the app after any renaming
- sources: which fetchers/processors provide it
- required: whether the ML model needs it (vs nice-to-have)
- default: fill value when missing (None = leave as NaN)

Rules:
- Fetchers output columns matching canonical_name exactly
- DataMerger joins on these names
- ML model reads these names — never hardcodes column strings elsewhere
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional

# ─── Sources ────────────────────────────────────────────────────────────────
# String constants so nothing is hardcoded elsewhere
SOURCE_HTAG = "htag_upload"
SOURCE_SEIFA = "abs_seifa"
SOURCE_ERP = "abs_erp"
SOURCE_BUILDING = "abs_building_approvals"
SOURCE_CENSUS = "abs_census"
SOURCE_NSW_SALES = "nsw_vg_sales"
SOURCE_VIC_SALES = "vic_sales"
SOURCE_QLD_SALES = "qld_sales"
SOURCE_RENTAL_GOV = "rental_government"
SOURCE_ACARA = "acara_schools"
SOURCE_DOMAIN_LISTINGS = "domain_listings"
SOURCE_DOMAIN_RENTAL = "domain_rental_avm"
SOURCE_AMENITIES = "amenities"
SOURCE_TRANSPORT = "transport"
SOURCE_HEALTHCARE = "healthcare"
SOURCE_CRIME = "crime"
SOURCE_EMPLOYMENT = "employment"
SOURCE_FLOOD_RISK = "flood_risk"
SOURCE_WALKABILITY = "walkability"


@dataclass
class ColumnSpec:
    canonical_name: str
    sources: List[str]
    required: bool = False       # ML model needs this to function
    default: Optional[Any] = None
    description: str = ""


# ─── Schema ─────────────────────────────────────────────────────────────────

SCHEMA: List[ColumnSpec] = [

    # ── Identity / Join Keys ─────────────────────────────────────────────
    ColumnSpec("Suburb",        [SOURCE_HTAG, SOURCE_NSW_SALES, SOURCE_VIC_SALES,
                                  SOURCE_RENTAL_GOV, SOURCE_ACARA, SOURCE_DOMAIN_LISTINGS],
               required=True, description="Suburb name (title case)"),
    ColumnSpec("State",         [SOURCE_HTAG, SOURCE_NSW_SALES, SOURCE_VIC_SALES,
                                  SOURCE_RENTAL_GOV, SOURCE_ACARA, SOURCE_DOMAIN_LISTINGS],
               required=True, description="State abbreviation (NSW, VIC, etc.)"),
    ColumnSpec("sa2_code",      [SOURCE_SEIFA, SOURCE_ERP, SOURCE_BUILDING, SOURCE_CENSUS],
               required=False, default=None, description="ABS SA2 code (9 digits, zero-padded)"),
    ColumnSpec("Region",        [SOURCE_HTAG], default="Unknown",
               description="SA4 or region name"),

    # ── Core Property Metrics (from HtAG/CSV upload) ─────────────────────
    ColumnSpec("Median Price",              [SOURCE_HTAG], required=True, default=500000,
               description="Median house sale price ($)"),
    ColumnSpec("Rental Yield on Houses",    [SOURCE_HTAG], required=True, default=4.0,
               description="Gross rental yield on houses (%)"),
    ColumnSpec("Distance (km) to CBD",      [SOURCE_HTAG], default=25.0,
               description="Distance from suburb to nearest CBD (km)"),
    ColumnSpec("Population",                [SOURCE_HTAG, SOURCE_ERP], default=15000,
               description="Suburb population (may be overridden by ERP)"),
    ColumnSpec("Vacancy Rate",              [SOURCE_HTAG], default=3.0,
               description="Rental vacancy rate (%)"),
    ColumnSpec("Sales Days on Market",      [SOURCE_HTAG], default=35,
               description="Median days on market for sales"),
    ColumnSpec("10 yr Avg. Annual Growth",  [SOURCE_HTAG], default=None,
               description="10-year average annual capital growth rate (%). "
                           "Only available from HtAG/manual upload — no free API equivalent."),

    # ── ABS SEIFA ─────────────────────────────────────────────────────────
    ColumnSpec("seifa_irsd_score",      [SOURCE_SEIFA], default=None,
               description="SEIFA Index of Relative Socio-economic Disadvantage score (~1000 = national average)"),
    ColumnSpec("seifa_irsd_decile",     [SOURCE_SEIFA], default=None,
               description="IRSD decile (1=most disadvantaged, 10=least)"),
    ColumnSpec("seifa_irsad_score",     [SOURCE_SEIFA], default=None,
               description="SEIFA Index of Relative Socio-economic Advantage and Disadvantage score"),
    ColumnSpec("seifa_irsad_decile",    [SOURCE_SEIFA], default=None,
               description="IRSAD decile (1=most disadvantaged, 10=most advantaged)"),
    ColumnSpec("seifa_ieo_score",       [SOURCE_SEIFA], default=None,
               description="SEIFA Index of Education and Occupation score"),
    ColumnSpec("seifa_ieo_decile",      [SOURCE_SEIFA], default=None,
               description="IEO decile"),
    ColumnSpec("seifa_ier_score",       [SOURCE_SEIFA], default=None,
               description="SEIFA Index of Economic Resources score"),
    ColumnSpec("seifa_ier_decile",      [SOURCE_SEIFA], default=None,
               description="IER decile"),

    # ── ABS ERP (Population) ──────────────────────────────────────────────
    ColumnSpec("erp_population",        [SOURCE_ERP], default=None,
               description="ABS Estimated Resident Population (latest year)"),
    ColumnSpec("erp_year",              [SOURCE_ERP], default=None,
               description="Year of ERP estimate"),
    ColumnSpec("pop_growth_rate_5yr",   [SOURCE_ERP], default=None,
               description="5-year compound annual population growth rate (%)"),

    # ── ABS Building Approvals ────────────────────────────────────────────
    ColumnSpec("total_approvals_12m",       [SOURCE_BUILDING], default=None,
               description="Total new dwelling approvals in last 12 months"),
    ColumnSpec("avg_monthly_approvals",     [SOURCE_BUILDING], default=None,
               description="Average monthly new dwelling approvals"),

    # ── ABS Census ────────────────────────────────────────────────────────
    ColumnSpec("median_age",                    [SOURCE_CENSUS], default=None,
               description="Median age of residents"),
    ColumnSpec("median_mortgage_monthly",       [SOURCE_CENSUS], default=None,
               description="Median monthly mortgage repayment ($)"),
    ColumnSpec("median_rent_weekly_census",     [SOURCE_CENSUS], default=None,
               description="Median weekly rent from Census 2021 ($)"),
    ColumnSpec("median_personal_income_weekly", [SOURCE_CENSUS], default=None,
               description="Median weekly personal income from Census 2021 ($)"),
    ColumnSpec("median_household_income_weekly",[SOURCE_CENSUS], default=None,
               description="Median weekly household income from Census 2021 ($)"),
    ColumnSpec("avg_household_size",            [SOURCE_CENSUS], default=None,
               description="Average household size (persons)"),
    ColumnSpec("owner_occupied_dwellings",      [SOURCE_CENSUS], default=None,
               description="Count of owner-occupied dwellings"),
    ColumnSpec("rented_dwellings",              [SOURCE_CENSUS], default=None,
               description="Count of rented dwellings"),
    ColumnSpec("owner_occupied_pct",            [SOURCE_CENSUS], default=None,
               description="Percentage of dwellings owner-occupied"),
    ColumnSpec("rented_pct",                    [SOURCE_CENSUS], default=None,
               description="Percentage of dwellings rented"),
    ColumnSpec("separate_houses",               [SOURCE_CENSUS], default=None,
               description="Count of separate houses"),
    ColumnSpec("flat_apartment_dwellings",      [SOURCE_CENSUS], default=None,
               description="Count of flats and apartments"),

    # ── Sales Data ────────────────────────────────────────────────────────
    ColumnSpec("nsw_median_sale_price", [SOURCE_NSW_SALES], default=None,
               description="Median property sale price from NSW Valuer General ($)"),
    ColumnSpec("nsw_sale_count",        [SOURCE_NSW_SALES], default=None,
               description="Number of sales in NSW VG dataset"),
    ColumnSpec("vic_median_sale_price", [SOURCE_VIC_SALES], default=None,
               description="Median property sale price from VIC Consumer Affairs ($)"),

    # ── Rental Data ───────────────────────────────────────────────────────
    ColumnSpec("median_rent_weekly_actual", [SOURCE_RENTAL_GOV], default=None,
               description="Median weekly rent from state government bond data ($)"),

    # ── ACARA Schools ─────────────────────────────────────────────────────
    ColumnSpec("school_quality_score",  [SOURCE_ACARA], default=None,
               description="Composite school quality 0–10 (ICSEA + NAPLAN equally weighted; uses whichever available)"),
    ColumnSpec("school_icsea_median",   [SOURCE_ACARA], default=None,
               description="Median ICSEA score across all schools in suburb (500–1300, national mean ~1000)"),
    ColumnSpec("naplan_mean_score",     [SOURCE_ACARA], default=None,
               description="Mean NAPLAN score (Reading + Numeracy, all year levels) across suburb schools"),
    ColumnSpec("school_count",          [SOURCE_ACARA], default=None,
               description="Total number of schools in suburb"),
    ColumnSpec("primary_count",         [SOURCE_ACARA], default=None,
               description="Number of primary schools in suburb"),
    ColumnSpec("secondary_count",       [SOURCE_ACARA], default=None,
               description="Number of secondary/combined schools in suburb"),
    ColumnSpec("pct_independent",       [SOURCE_ACARA], default=None,
               description="Percentage of schools that are Independent/Private (0–100)"),
    ColumnSpec("pct_catholic",          [SOURCE_ACARA], default=None,
               description="Percentage of schools that are Catholic (0–100)"),
    ColumnSpec("pct_government",        [SOURCE_ACARA], default=None,
               description="Percentage of schools that are Government/Public (0–100)"),
    ColumnSpec("has_secondary",         [SOURCE_ACARA], default=None,
               description="True if suburb has at least one secondary or combined school"),

    # ── Domain API ────────────────────────────────────────────────────────
    ColumnSpec("domain_median_list_price",      [SOURCE_DOMAIN_LISTINGS], default=None,
               description="Median listed sale price from Domain current listings ($)"),
    ColumnSpec("domain_listing_count",          [SOURCE_DOMAIN_LISTINGS], default=None,
               description="Number of current active listings on Domain"),
    ColumnSpec("domain_median_bedrooms",        [SOURCE_DOMAIN_LISTINGS], default=None,
               description="Median bedroom count in current Domain listings"),
    ColumnSpec("domain_median_rental_estimate", [SOURCE_DOMAIN_RENTAL], default=None,
               description="Median weekly rental estimate from Domain Rental AVM ($)"),
    ColumnSpec("domain_rental_sample_size",     [SOURCE_DOMAIN_RENTAL], default=None,
               description="Number of properties used in Domain rental AVM aggregation"),

    # ── QLD Sales ─────────────────────────────────────────────────────────────
    ColumnSpec("qld_median_sale_price", [SOURCE_QLD_SALES], default=None,
               description="Median residential sale price from QLD Titles Registry ($)"),
    ColumnSpec("qld_sale_count",        [SOURCE_QLD_SALES], default=None,
               description="Number of residential sales in QLD dataset"),
    ColumnSpec("qld_median_land_size",  [SOURCE_QLD_SALES], default=None,
               description="Median land size from QLD sales data (m²)"),

    # ── Amenities (OpenStreetMap) ──────────────────────────────────────────────
    ColumnSpec("amenity_score",         [SOURCE_AMENITIES], default=None,
               description="Composite lifestyle amenity score 0-10 (cafes, shops, parks, gyms)"),
    ColumnSpec("cafe_count",            [SOURCE_AMENITIES], default=None,
               description="Number of cafes in suburb (OSM)"),
    ColumnSpec("supermarket_count",     [SOURCE_AMENITIES], default=None,
               description="Number of supermarkets/groceries in suburb (OSM)"),
    ColumnSpec("park_count",            [SOURCE_AMENITIES], default=None,
               description="Number of parks/gardens in suburb (OSM)"),
    ColumnSpec("restaurant_count",      [SOURCE_AMENITIES], default=None,
               description="Number of restaurants in suburb (OSM)"),
    ColumnSpec("gym_count",             [SOURCE_AMENITIES], default=None,
               description="Number of gyms/fitness centres in suburb (OSM)"),

    # ── Public Transport (OpenStreetMap) ──────────────────────────────────────
    ColumnSpec("transit_score",         [SOURCE_TRANSPORT], default=None,
               description="Public transport access score 0-10 (weighted stops: rail > bus)"),
    ColumnSpec("train_station_count",   [SOURCE_TRANSPORT], default=None,
               description="Number of train stations/halts in suburb (OSM)"),
    ColumnSpec("bus_stop_count",        [SOURCE_TRANSPORT], default=None,
               description="Number of bus stops in suburb (OSM)"),
    ColumnSpec("tram_stop_count",       [SOURCE_TRANSPORT], default=None,
               description="Number of tram stops in suburb (OSM)"),
    ColumnSpec("has_train_station",     [SOURCE_TRANSPORT], default=None,
               description="Whether suburb has at least one train/subway station"),

    # ── Healthcare (OSM + AIHW) ───────────────────────────────────────────────
    ColumnSpec("healthcare_score",      [SOURCE_HEALTHCARE], default=None,
               description="Healthcare access score 0-10 (hospitals, GPs, pharmacies)"),
    ColumnSpec("hospital_count",        [SOURCE_HEALTHCARE], default=None,
               description="Number of hospitals in or near suburb"),
    ColumnSpec("clinic_count",          [SOURCE_HEALTHCARE], default=None,
               description="Number of GP clinics/health centres in suburb (OSM)"),
    ColumnSpec("pharmacy_count",        [SOURCE_HEALTHCARE], default=None,
               description="Number of pharmacies in suburb (OSM)"),

    # ── Crime (BOCSAR NSW + VIC Crime Stats) ───────────────────────────────────
    ColumnSpec("crime_risk_score",          [SOURCE_CRIME], default=None,
               description="Crime risk score 0-10 (lower = safer), normalised from offence rate"),
    ColumnSpec("crime_incidents_per_1000",  [SOURCE_CRIME], default=None,
               description="Total recorded offences per 1,000 population (LGA level)"),
    ColumnSpec("property_offences",         [SOURCE_CRIME], default=None,
               description="Number of property-related offences (break-in, theft, robbery)"),

    # ── Employment (ABS Census 2021) ───────────────────────────────────────────
    ColumnSpec("employment_score",                  [SOURCE_EMPLOYMENT], default=None,
               description="Employment conditions score 0-10 (lower unemployment = higher)"),
    ColumnSpec("unemployment_rate",                 [SOURCE_EMPLOYMENT], default=None,
               description="Unemployment rate (% of labour force) from ABS Census 2021"),
    ColumnSpec("labour_force_participation_rate",   [SOURCE_EMPLOYMENT], default=None,
               description="Labour force participation rate (% of working-age population)"),

    # ── Flood & Bushfire Risk ──────────────────────────────────────────────────
    ColumnSpec("flood_risk_score",      [SOURCE_FLOOD_RISK], default=None,
               description="Flood risk score 0-10 (lower = lower risk)"),
    ColumnSpec("bushfire_risk_score",   [SOURCE_FLOOD_RISK], default=None,
               description="Bushfire risk score 0-10 (lower = lower risk)"),
    ColumnSpec("natural_hazard_risk",   [SOURCE_FLOOD_RISK], default=None,
               description="Composite natural hazard risk 0-10 (flood + bushfire equally weighted)"),

    # ── Walkability (OpenStreetMap) ────────────────────────────────────────────
    ColumnSpec("walkability_score",     [SOURCE_WALKABILITY], default=None,
               description="Walk Score-style walkability index 0-100 (OSM amenity density)"),
    ColumnSpec("bike_score",            [SOURCE_WALKABILITY], default=None,
               description="Cycling infrastructure score 0-10 (cycleway density from OSM)"),
    ColumnSpec("is_walkable",           [SOURCE_WALKABILITY], default=None,
               description="True if walkability_score >= 70"),
    ColumnSpec("is_bikeable",           [SOURCE_WALKABILITY], default=None,
               description="True if bike_score >= 6"),
]

# ─── Lookup helpers ──────────────────────────────────────────────────────────

_BY_NAME = {s.canonical_name: s for s in SCHEMA}

# All canonical column names
ALL_COLUMNS = [s.canonical_name for s in SCHEMA]

# Columns the ML model uses as input features
ML_FEATURE_COLUMNS = [s.canonical_name for s in SCHEMA if s.canonical_name not in
                       ("Suburb", "State", "sa2_code", "Region", "erp_year",
                        "nsw_sale_count", "domain_rental_sample_size")]

# Columns that come from SA2-keyed sources (joined via sa2_code)
SA2_KEYED_COLUMNS = [s.canonical_name for s in SCHEMA
                      if any(src in (SOURCE_SEIFA, SOURCE_ERP, SOURCE_BUILDING, SOURCE_CENSUS)
                             for src in s.sources)]

# Columns that come from suburb+state-keyed sources
SUBURB_KEYED_COLUMNS = [s.canonical_name for s in SCHEMA
                         if any(src in (SOURCE_NSW_SALES, SOURCE_VIC_SALES, SOURCE_RENTAL_GOV,
                                        SOURCE_ACARA, SOURCE_DOMAIN_LISTINGS, SOURCE_DOMAIN_RENTAL)
                                for src in s.sources)
                         and s.canonical_name not in ("Suburb", "State")]


def get_spec(column_name: str) -> ColumnSpec:
    return _BY_NAME[column_name]


def columns_for_source(source: str) -> List[str]:
    return [s.canonical_name for s in SCHEMA if source in s.sources]


def default_for(column_name: str) -> Optional[Any]:
    spec = _BY_NAME.get(column_name)
    return spec.default if spec else None


def validate_dataframe(df) -> dict:
    """
    Check a DataFrame against the schema.
    Returns dict with present, missing_required, missing_optional, unknown columns.
    """
    import pandas as pd
    required = [s.canonical_name for s in SCHEMA if s.required]
    optional = [s.canonical_name for s in SCHEMA if not s.required]
    known = set(ALL_COLUMNS)

    present = [c for c in ALL_COLUMNS if c in df.columns]
    missing_required = [c for c in required if c not in df.columns]
    missing_optional = [c for c in optional if c not in df.columns]
    unknown = [c for c in df.columns if c not in known]

    return {
        "present": present,
        "missing_required": missing_required,
        "missing_optional_count": len(missing_optional),
        "unknown_columns": unknown,
        "enrichment_coverage": {
            c: f"{df[c].notna().mean():.0%}" for c in present
            if c not in ("Suburb", "State", "sa2_code", "Region")
        },
    }
