# Medelite Facility Assessment Report Generator
This application integrates multiple CMS Nursing Home datasets, including Provider Information, Claims-Based Quality Measures, and State & US Averages, to generate a Facility Assessment Snapshot. Operational fields such as EMR, patient type, and Medelite history are intentionally captured as manual inputs because they represent internal business information and are not available in CMS public datasets.

A Streamlit micro-app for the Medelite Healthcare Data Automation & QA Analytics case study.

## What it does

- Accepts a CMS Certification Number (CCN)
- Looks up facility metadata and star ratings from the CMS Provider Information dataset
- Pulls facility-level hospitalization/ED measures from CMS Medicare Claims Quality Measures
- Pulls state and national benchmark values from CMS State & US Averages
- Combines CMS fields with manual Medelite operational inputs
- Generates a polished, print-ready PDF with the required branding and a Medicare Care Compare hyperlink

## Required data files

The app expects these files in the `data/` folder:

```text
data/provider_information.csv
data/claims_quality_measures.csv
data/state_us_averages.csv
```

These correspond to:

- Provider Information: `4pq5-n9py`
- Medicare Claims Quality Measures: `ijh5-nb2v`
- State & US Averages: `xcdc-v8bm`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Test CCN

```text
686123
```

## Field mapping

- Name, location, beds, and star ratings: Provider Information
- STR/LT hospitalization and ED facility metrics: Medicare Claims Quality Measures
- STR/LT hospitalization and ED state/national averages: State & US Averages
- EMR, current census, patient type, Medelite history, and medical coverage: manual operational inputs

## Assumptions

- The app uses official CMS CSV exports placed locally in the repository for deployment stability.
- If a metric is unavailable or missing in the CMS export, the PDF displays `N/A` rather than inventing a value.
- Current Census is treated as a Medelite manual operational input, per the technical brief.
