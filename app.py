import streamlit as st

from services.cms_service import CMSService
from services.report_service import ReportService
from services.validators import validate_report


st.set_page_config(page_title="Medelite Facility Assessment", layout="wide")

st.markdown(
    """
    <div style="padding: 18px; border-radius: 12px; background-color: #111827; color: white; margin-bottom: 18px;">
        <h1 style="margin: 0; font-size: 30px;">INFINITE — Managed by MEDELITE</h1>
        <h3 style="margin: 6px 0 0 0; font-weight: 500;">FACILITY ASSESSMENT SNAPSHOT</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Enter a CMS Certification Number (CCN) to generate a facility assessment report. "
    "CMS facility metadata, ratings, hospitalization metrics, and state/national benchmarks are populated from the loaded CMS datasets."
)

@st.cache_resource
def load_cms_service():
    return CMSService()

cms_service = load_cms_service()
report_service = ReportService()

if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "last_ccn" not in st.session_state:
    st.session_state.last_ccn = ""

ccn = st.text_input("Enter CCN", placeholder="Example: 686123")

if st.button("Lookup Facility", type="primary"):
    if not ccn.strip():
        st.error("Please enter a CCN.")
    else:
        report_data = cms_service.get_full_report_data(ccn)
        if report_data is None:
            st.session_state.report_data = None
            st.error("Facility not found. Please verify the CCN and try again.")
        else:
            st.session_state.report_data = report_data
            st.session_state.last_ccn = ccn.strip()
            st.success("Facility found and CMS metrics loaded.")

report_data = st.session_state.report_data

if report_data:
    st.divider()

    st.subheader(f"Facility Preview: {report_data['official_name']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("State", report_data["state"])
    c2.metric("Certified Beds", report_data["census_capacity"])
    c3.metric("Overall Rating", report_data["overall_rating"])
    c4.metric("QM Rating", report_data["quality_of_resident_care"])

    st.caption(
        f"Medicare Care Compare: https://www.medicare.gov/care-compare/details/nursing-home/{report_data['ccn']}"
    )

    st.subheader("Manual Operational Inputs")
    st.caption("These fields are internal Medelite operational inputs and are not sourced from CMS.")

    col1, col2 = st.columns(2)

    with col1:
        facility_name = st.text_input(
            "Facility Name Override",
            value=report_data["official_name"],
            help="Override the CMS provider name if Medelite uses a localized/internal facility name.",
        )
        emr = st.text_input("EMR", value="", placeholder="e.g. PointClickCare, MatrixCare")
        current_census = st.number_input(
            "Current Census",
            min_value=0,
            value=0,
            help="Manual input. CMS average residents per day is shown in the facility preview only."
        )
        patient_type = st.text_input("Type of Patient", value="", placeholder="e.g. Long-term & Short-term")

    with col2:
        previous_coverage = st.selectbox("Previous Coverage from Medelite", ["", "Yes", "No"], index=0)
        provider_performance = st.text_input(
            "Previous Provider Performance from Medelite",
            value="",
            placeholder="e.g. About 30 patients/day",
        )
        medical_coverage = st.text_input(
            "Medical Coverage",
            value="",
            placeholder="e.g. Optometry, PCP, Podiatry",
        )

    manual_data = {
        "facility_name": facility_name,
        "emr": emr,
        "current_census": current_census,
        "patient_type": patient_type,
        "previous_coverage": previous_coverage,
        "provider_performance": provider_performance,
        "medical_coverage": medical_coverage,
    }

    st.subheader("Automatically Populated Hospitalization & ED Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STR Hospitalization", report_data["str_hosp"])
    m2.metric("STR ED Visit", report_data["str_ed"])
    m3.metric("LT Hospitalization", report_data["lt_hosp"])
    m4.metric("LT ED Visit", report_data["lt_ed"])

    with st.expander("Show all report fields"):
        st.write("Facility and Ratings")
        st.table({
            "Field": [
                "Name of Facility", "Location", "Census Capacity", "Overall Star Rating",
                "Health Inspection", "Staffing", "Quality of Resident Care"
            ],
            "Value": [
                manual_data["facility_name"], report_data["location"], report_data["census_capacity"],
                report_data["overall_rating"], report_data["health_inspection"], report_data["staffing"],
                report_data["quality_of_resident_care"]
            ]
        })
        st.write("Hospitalization & ED Metrics")
        st.table({
            "Field": [
                "Short Term Hospitalization", "STR National Avg. for Hospitalization", "STR State Avg. for Hospitalization",
                "STR ED Visit", "STR ED Visits National Avg.", "STR ED Visits State Avg.",
                "LT Hospitalization", "LT National Avg. for Hospitalization", "LT State Avg. for Hospitalization",
                "ED Visit", "LT ED Visits National Avg.", "LT ED Visits State Avg."
            ],
            "Value": [
                report_data["str_hosp"], report_data["str_hosp_nat"], report_data["str_hosp_state"],
                report_data["str_ed"], report_data["str_ed_nat"], report_data["str_ed_state"],
                report_data["lt_hosp"], report_data["lt_hosp_nat"], report_data["lt_hosp_state"],
                report_data["lt_ed"], report_data["lt_ed_nat"], report_data["lt_ed_state"]
            ]
        })

    st.subheader("QA Validation")
    warnings = validate_report(report_data, manual_data)
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("QA checks passed.")

    pdf_buffer = report_service.generate_pdf(report_data, manual_data)
    st.download_button(
        "Download PDF",
        data=pdf_buffer,
        file_name=f"{report_data['ccn']}_facility_assessment_snapshot.pdf",
        mime="application/pdf",
        type="primary",
    )
