import csv
from pathlib import Path


class CMSService:
    """Reads official CMS Provider Data Catalog CSV exports and maps them to the report."""

    PROVIDER_FILE = Path("data/provider_information.csv")
    CLAIMS_FILE = Path("data/claims_quality_measures.csv")
    STATE_AVG_FILE = Path("data/state_us_averages.csv")

    def __init__(self):
        self.provider_rows = self._read_csv(self.PROVIDER_FILE)
        self.claims_rows = self._read_csv(self.CLAIMS_FILE)
        self.state_average_rows = self._read_csv(self.STATE_AVG_FILE)

    def _read_csv(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Required data file missing: {path}")
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def clean(value):
        if value is None:
            return "N/A"
        value = str(value).strip()
        return value if value else "N/A"

    @staticmethod
    def format_percent(value):
        value = str(value).strip()
        if not value:
            return "N/A"
        if value.endswith("%"):
            return value
        try:
            return f"{float(value):.1f}%"
        except ValueError:
            return value

    @staticmethod
    def format_number(value, decimals=2):
        value = str(value).strip()
        if not value:
            return "N/A"
        try:
            return f"{float(value):.{decimals}f}"
        except ValueError:
            return value

    def get_provider_by_ccn(self, ccn: str):
        ccn = str(ccn).strip()
        for row in self.provider_rows:
            if str(row.get("CMS Certification Number (CCN)", "")).strip() == ccn:
                return row
        return None

    def get_claims_metrics_by_ccn(self, ccn: str):
        ccn = str(ccn).strip()
        metrics = {
            "str_hosp": "N/A",
            "str_ed": "N/A",
            "lt_hosp": "N/A",
            "lt_ed": "N/A",
        }

        for row in self.claims_rows:
            if str(row.get("CMS Certification Number (CCN)", "")).strip() != ccn:
                continue

            code = str(row.get("Measure Code", "")).strip()
            score = row.get("Adjusted Score", "")

            if code == "521":
                metrics["str_hosp"] = self.format_percent(score)
            elif code == "522":
                metrics["str_ed"] = self.format_percent(score)
            elif code == "551":
                metrics["lt_hosp"] = self.format_number(score, 2)
            elif code == "552":
                metrics["lt_ed"] = self.format_number(score, 2)

        return metrics

    def get_state_and_nation_averages(self, state: str):
        state = str(state).strip().upper()

        metrics = {
            "str_hosp_nat": "N/A",
            "str_hosp_state": "N/A",
            "str_ed_nat": "N/A",
            "str_ed_state": "N/A",
            "lt_hosp_nat": "N/A",
            "lt_hosp_state": "N/A",
            "lt_ed_nat": "N/A",
            "lt_ed_state": "N/A",
        }

        state_row = None
        nation_row = None

        for row in self.state_average_rows:
            state_or_nation = str(row.get("State or Nation", "")).strip().upper()
            if state_or_nation == state:
                state_row = row
            elif state_or_nation == "NATION":
                nation_row = row

        metric_columns = {
            "str_hosp": "Percentage of short stay residents who were rehospitalized after a nursing home admission",
            "str_ed": "Percentage of short stay residents who had an outpatient emergency department visit",
            "lt_hosp": "Number of hospitalizations per 1000 long-stay resident days",
            "lt_ed": "Number of outpatient emergency department visits per 1000 long-stay resident days",
        }

        if state_row:
            metrics["str_hosp_state"] = self.format_percent(state_row.get(metric_columns["str_hosp"], ""))
            metrics["str_ed_state"] = self.format_percent(state_row.get(metric_columns["str_ed"], ""))
            metrics["lt_hosp_state"] = self.format_number(state_row.get(metric_columns["lt_hosp"], ""), 2)
            metrics["lt_ed_state"] = self.format_number(state_row.get(metric_columns["lt_ed"], ""), 2)

        if nation_row:
            metrics["str_hosp_nat"] = self.format_percent(nation_row.get(metric_columns["str_hosp"], ""))
            metrics["str_ed_nat"] = self.format_percent(nation_row.get(metric_columns["str_ed"], ""))
            metrics["lt_hosp_nat"] = self.format_number(nation_row.get(metric_columns["lt_hosp"], ""), 2)
            metrics["lt_ed_nat"] = self.format_number(nation_row.get(metric_columns["lt_ed"], ""), 2)

        return metrics

    def get_full_report_data(self, ccn: str):
        provider = self.get_provider_by_ccn(ccn)
        if provider is None:
            return None

        claims = self.get_claims_metrics_by_ccn(ccn)
        averages = self.get_state_and_nation_averages(provider.get("State", ""))

        location = provider.get("Location", "")
        if not location:
            location = ", ".join(
                part for part in [
                    provider.get("Provider Address", ""),
                    provider.get("City/Town", ""),
                    provider.get("State", ""),
                ] if part
            )

        return {
            "ccn": self.clean(provider.get("CMS Certification Number (CCN)")),
            "state": self.clean(provider.get("State")),
            "official_name": self.clean(provider.get("Provider Name")),
            "legal_business_name": self.clean(provider.get("Legal Business Name")),
            "location": self.clean(location),
            "census_capacity": self.clean(provider.get("Number of Certified Beds")),
            "average_residents_per_day": self.clean(provider.get("Average Number of Residents per Day")),
            "overall_rating": self.clean(provider.get("Overall Rating")),
            "health_inspection": self.clean(provider.get("Health Inspection Rating")),
            "staffing": self.clean(provider.get("Staffing Rating")),
            "quality_of_resident_care": self.clean(provider.get("QM Rating")),
            **claims,
            **averages,
        }
