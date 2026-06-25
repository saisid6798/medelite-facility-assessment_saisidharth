def validate_report(report_data, manual_data):
    warnings = []

    if not report_data:
        return ["No facility data found."]

    for label in ["overall_rating", "health_inspection", "staffing", "quality_of_resident_care"]:
        value = str(report_data.get(label, "")).strip()
        if value not in {"1", "2", "3", "4", "5"}:
            warnings.append(f"{label.replace('_', ' ').title()} is missing or outside the expected 1–5 range.")

    try:
        beds = float(report_data.get("census_capacity", 0))
        census = float(manual_data.get("current_census", 0))
        if census > beds:
            warnings.append("Current Census is greater than Census Capacity.")
    except Exception:
        warnings.append("Could not validate Current Census against Census Capacity.")

    missing_optional = []
    for key in [
        "str_hosp", "str_hosp_nat", "str_hosp_state", "str_ed", "str_ed_nat", "str_ed_state",
        "lt_hosp", "lt_hosp_nat", "lt_hosp_state", "lt_ed", "lt_ed_nat", "lt_ed_state",
    ]:
        if str(report_data.get(key, "N/A")).strip().upper() == "N/A":
            missing_optional.append(key)

    if missing_optional:
        warnings.append("Some hospitalization/ED metrics are unavailable and will display as N/A.")

    return warnings
