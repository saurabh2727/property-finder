from services.data_fetcher.abs_building_approvals_fetcher import ABSBuildingApprovalsFetcher
from services.data_fetcher.abs_census_fetcher import ABSCensusFetcher
from services.data_fetcher.abs_erp_fetcher import ABSERPFetcher
from services.data_fetcher.abs_seifa_fetcher import ABSSEIFAFetcher
from services.data_fetcher.acara_schools_fetcher import ACARASchoolsFetcher
from services.data_fetcher.base_fetcher import BaseFetcher
from services.data_fetcher.data_merger import DataMerger
from services.data_fetcher.domain_fetcher import DomainListingsFetcher, DomainRentalAVMFetcher
from services.data_fetcher.nsw_sales_fetcher import NSWSalesFetcher
from services.data_fetcher.rental_data_fetcher import RentalDataFetcher
from services.data_fetcher.sa2_concordance import SA2Concordance
from services.data_fetcher.vic_sales_fetcher import VICSalesFetcher

__all__ = [
    "BaseFetcher",
    "ABSSEIFAFetcher",
    "ABSCensusFetcher",
    "ABSERPFetcher",
    "ABSBuildingApprovalsFetcher",
    "ACARASchoolsFetcher",
    "NSWSalesFetcher",
    "VICSalesFetcher",
    "RentalDataFetcher",
    "DomainListingsFetcher",
    "DomainRentalAVMFetcher",
    "SA2Concordance",
    "DataMerger",
]
