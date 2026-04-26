from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AUTOMATED CONGESTION AND CURTAILMENT SCREENING VIEWER FOR ALBERTA TRANSMISSION GRID",
    layout="wide",
)

APP_DIR = Path(__file__).resolve().parent


def find_first_existing(patterns):
    for pattern in patterns:
        matches = sorted(APP_DIR.glob(pattern))
        if matches:
            return matches[0]
    return None


DEFAULT_N0_FILE = find_first_existing([
    "N0_Report_Summary*.xlsx",
    "*N0*Report*.xlsx",
    "*.xlsx",
])
DEFAULT_GEN_ZIP = find_first_existing([
    "generator_outputs*.zip",
    "*generator*.zip",
    "*.zip",
])
DEFAULT_GEN_ADJ_FILE = find_first_existing([
    "gen_adj_hourly*.csv",
    "*gen*adj*.csv",
])
DEFAULT_VIDEO_FILE = find_first_existing([
    "Demo_Video*.mp4",
    "*demo*.mp4",
    "*.mp4",
])


st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.45rem;
        font-weight: 800;
        color: #16325c;
        line-height: 1.2;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        color: #5d6b82;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    .section-box {
        background: linear-gradient(135deg, #f7fbff 0%, #eef5ff 100%);
        border: 1px solid #d6e5ff;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 22px rgba(22, 50, 92, 0.08);
        margin-bottom: 1rem;
    }
    .insight-heading {
        font-size: 1.35rem;
        font-weight: 700;
        color: #16325c;
        margin-bottom: 0.25rem;
    }
    .insight-subtext {
        color: #5d6b82;
        margin-bottom: 0.9rem;
    }
    .insight-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(180px, 1fr));
        gap: 14px;
    }
    .insight-card {
        border-radius: 16px;
        padding: 16px 18px;
        color: #14233b;
        box-shadow: 0 10px 20px rgba(22, 50, 92, 0.10);
        border: 1px solid rgba(255,255,255,0.55);
    }
    .insight-card.blue {
        background: linear-gradient(135deg, #eef6ff 0%, #d7e9ff 100%);
        border-left: 6px solid #3b82f6;
    }
    .insight-card.green {
        background: linear-gradient(135deg, #eefcf5 0%, #d8f4e4 100%);
        border-left: 6px solid #22a06b;
    }
    .insight-card.orange {
        background: linear-gradient(135deg, #fff8ec 0%, #ffe3bd 100%);
        border-left: 6px solid #f59e0b;
    }
    .insight-card.red {
        background: linear-gradient(135deg, #fff1f0 0%, #ffd8d3 100%);
        border-left: 6px solid #dc2626;
    }
    .insight-card.purple {
        background: linear-gradient(135deg, #f5f0ff 0%, #e3d8ff 100%);
        border-left: 6px solid #7c3aed;
    }
    .insight-label {
        font-size: 0.92rem;
        font-weight: 600;
        color: #344767;
        margin-bottom: 0.25rem;
    }
    .insight-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #13233a;
        margin-bottom: 0.18rem;
        line-height: 1.1;
    }
    .insight-note {
        font-size: 0.86rem;
        color: #495d7a;
    }
    .small-note {
        color: #6a7b96;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eff5ff 0%, #e4eefc 100%);
        border-right: 1px solid #d7e4fb;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #16325c;
        font-weight: 800;
    }
    .sidebar-panel {
        background: linear-gradient(135deg, #f9fbff 0%, #edf4ff 100%);
        border: 1px solid #d6e5ff;
        border-radius: 18px;
        padding: 14px 14px 8px 14px;
        box-shadow: 0 10px 24px rgba(22, 50, 92, 0.10);
        margin-bottom: 14px;
    }
    .sidebar-panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #16325c;
        margin-bottom: 0.35rem;
    }
    .sidebar-panel-note {
        color: #5d6b82;
        font-size: 0.88rem;
        margin-bottom: 0.35rem;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #f9fbff 0%, #edf4ff 100%);
        border: 1px solid #d6e5ff;
        border-radius: 18px;
        padding: 10px;
        box-shadow: 0 10px 20px rgba(22, 50, 92, 0.08);
        margin-bottom: 14px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #ffffff 0%, #f1f6ff 100%);
        border: 2px dashed #8db7ff;
        border-radius: 16px;
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #ffffff 0%, #e8f1ff 100%);
    }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stDownloadButton > button,
    [data-testid="stSidebar"] button[kind="secondary"] {
        border-radius: 12px;
        border: 1px solid #b8d0ff;
        background: linear-gradient(135deg, #ffffff 0%, #edf4ff 100%);
        color: #16325c;
        box-shadow: 0 6px 14px rgba(22, 50, 92, 0.08);
        font-weight: 600;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #203456;
    }
    .sidebar-file-line {
        background: rgba(255,255,255,0.78);
        border-left: 5px solid #3b82f6;
        border-radius: 12px;
        padding: 10px 12px;
        margin: 8px 0;
        box-shadow: 0 6px 14px rgba(22, 50, 92, 0.06);
    }
    .sidebar-file-name {
        color: #16325c;
        font-weight: 700;
    }
    .sidebar-file-label {
        color: #5d6b82;
        font-size: 0.86rem;
        margin-bottom: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_file_bytes(uploaded_file_bytes=None, fallback_path=None, required=True):
    if uploaded_file_bytes is not None:
        return uploaded_file_bytes
    if fallback_path is None:
        if required:
            raise FileNotFoundError("No file source provided.")
        return None
    path = Path(fallback_path)
    if not path.exists():
        if required:
            raise FileNotFoundError("File not found: {0}".format(path))
        return None
    return path.read_bytes()


@st.cache_data(show_spinner=False)
def load_n0_hourly_table(xlsx_bytes):
    raw = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name="Raw_Hourly")
    raw.columns = [str(c).strip() for c in raw.columns]

    if "time" not in raw.columns:
        raise ValueError("The Excel file must contain a 'Raw_Hourly' sheet with a 'time' column.")

    raw["time"] = pd.to_datetime(raw["time"], errors="coerce")
    raw = raw.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)

    if raw.empty:
        raise ValueError("The 'Raw_Hourly' sheet is empty after parsing time values.")

    year = int(raw["time"].dt.year.mode().iloc[0])
    full_hours = pd.DataFrame({
        "time": pd.date_range(start="{0}-01-01 00:00:00".format(year), end="{0}-12-31 23:00:00".format(year), freq="H")
    })
    full_hours["hour_no"] = range(1, len(full_hours) + 1)

    merged = full_hours.merge(raw, on="time", how="left")
    merged["n0_data_available"] = merged.drop(columns=["time", "hour_no"]).notna().any(axis=1)

    numeric_cols = [
        "max_loading_pre", "thermal_viol_pre", "voltage_viol_pre",
        "max_loading_post", "thermal_viol_post", "voltage_viol_post"
    ]
    for col in numeric_cols:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    return merged


@st.cache_data(show_spinner=False)
def load_excel_sheet_names(xlsx_bytes):
    xl = pd.ExcelFile(io.BytesIO(xlsx_bytes))
    return xl.sheet_names


@st.cache_data(show_spinner=False)
def load_sheet_preview(xlsx_bytes, sheet_name, nrows=20):
    return pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=sheet_name, nrows=nrows)


@st.cache_data(show_spinner=False)
def list_generators_from_zip(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = [Path(name).stem for name in zf.namelist() if name.lower().endswith(".csv")]
    return sorted(names)


@st.cache_data(show_spinner=False)
def load_generator_series(zip_bytes, generator_name, year):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        all_names = zf.namelist()
        match_map = {}
        for name in all_names:
            if name.lower().endswith(".csv"):
                match_map[Path(name).stem] = name

        if generator_name not in match_map:
            raise FileNotFoundError("Generator '{0}' not found in ZIP.".format(generator_name))

        with zf.open(match_map[generator_name]) as f:
            gen = pd.read_csv(f)

    gen.columns = [str(c).strip() for c in gen.columns]
    dt_col = next((c for c in gen.columns if c.lower() in ["datetime", "date", "time", "timestamp"]), None)
    val_col = next((c for c in gen.columns if c.upper() in ["GEN-ADJ", "GEN_ADJ", "GEN_ADJ_MW", "VALUE", "MW"]), None)

    if dt_col is None:
        raise ValueError("No DateTime-like column found in generator file for '{0}'.".format(generator_name))
    if val_col is None:
        raise ValueError("No generator value column found in generator file for '{0}'.".format(generator_name))

    gen = gen[[dt_col, val_col]].copy()
    gen.columns = ["DateTime", "GEN_ADJ"]
    gen["DateTime"] = pd.to_datetime(gen["DateTime"], errors="coerce")
    gen["GEN_ADJ"] = pd.to_numeric(gen["GEN_ADJ"], errors="coerce")
    gen = gen.dropna(subset=["DateTime"]).sort_values("DateTime").reset_index(drop=True)

    full_hours = pd.DataFrame({
        "DateTime": pd.date_range(start="{0}-01-01 00:00:00".format(year), end="{0}-12-31 23:00:00".format(year), freq="H")
    })
    full_hours["hour_no"] = range(1, len(full_hours) + 1)
    merged = full_hours.merge(gen, on="DateTime", how="left")
    merged["gen_data_available"] = merged["GEN_ADJ"].notna()
    return merged


@st.cache_data(show_spinner=False)
def load_total_curtailment_table(csv_bytes, year):
    if csv_bytes is None:
        return None

    df = pd.read_csv(io.BytesIO(csv_bytes))
    df.columns = [str(c).strip() for c in df.columns]

    dt_col = next((c for c in df.columns if c.lower() in ["hour", "datetime", "date", "time", "timestamp"]), None)
    val_col = next((c for c in df.columns if c.lower() in ["gen-adj sum (mw)", "gen_adj_sum_mw", "gen-adj", "gen_adj", "value", "mw"]), None)

    if dt_col is None or val_col is None:
        raise ValueError("The hourly curtailment CSV must contain a time column and a curtailment value column.")

    out = df[[dt_col, val_col]].copy()
    out.columns = ["Hour", "GEN_ADJ_SUM_MW"]

    parsed = pd.to_datetime(out["Hour"].astype(str), format="%Y%m%d_%H%M", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(out["Hour"], errors="coerce")

    out["DateTime"] = parsed
    out["GEN_ADJ_SUM_MW"] = pd.to_numeric(out["GEN_ADJ_SUM_MW"], errors="coerce")
    out = out.dropna(subset=["DateTime"]).sort_values("DateTime").reset_index(drop=True)

    full_hours = pd.DataFrame({
        "DateTime": pd.date_range(start="{0}-01-01 00:00:00".format(year), end="{0}-12-31 23:00:00".format(year), freq="H")
    })
    full_hours["hour_no"] = range(1, len(full_hours) + 1)
    merged = full_hours.merge(out[["DateTime", "GEN_ADJ_SUM_MW"]], on="DateTime", how="left")
    merged["total_curtailment_available"] = merged["GEN_ADJ_SUM_MW"].notna()
    return merged


def format_mw(value):
    if pd.isna(value):
        return "No data"
    return "{0:.2f} MW".format(float(value))


def format_num(value, decimals=2):
    if pd.isna(value):
        return "No data"
    return ("{0:." + str(decimals) + "f}").format(float(value))


def format_int_like(value):
    if pd.isna(value):
        return "No data"
    return str(int(float(value)))


def insight_class_for_loading(value):
    if pd.isna(value):
        return "blue"
    value = float(value)
    if value >= 100:
        return "red"
    if value >= 90:
        return "orange"
    return "green"


def insight_class_for_violations(value):
    if pd.isna(value):
        return "blue"
    return "red" if float(value) > 0 else "green"


def insight_class_for_curtailment(value):
    if pd.isna(value):
        return "blue"
    value = float(value)
    if value >= 100:
        return "purple"
    if value > 0:
        return "orange"
    return "green"


def render_insight_card(label, value, note, css_class="blue"):
    return """<div class='insight-card {0}'>
        <div class='insight-label'>{1}</div>
        <div class='insight-value'>{2}</div>
        <div class='insight-note'>{3}</div>
    </div>""".format(css_class, label, value, note)


st.markdown(
    "<div class='main-title'>AUTOMATED CONGESTION AND CURTAILMENT SCREENING VIEWER FOR ALBERTA TRANSMISSION GRID</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='sub-title'>N-0 hourly results, generator curtailment, total hourly curtailment, and demo video in one interactive dashboard.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("<div class='sidebar-panel'><div class='sidebar-panel-title'>Data source</div><div class='sidebar-panel-note'>Upload your dashboard files here or let the app use the local files detected in the same folder.</div></div>", unsafe_allow_html=True)

    n0_uploaded = st.file_uploader("Upload N-0 Excel file", type=["xlsx"])
    gen_uploaded = st.file_uploader("Upload generator ZIP file", type=["zip"])
    total_adj_uploaded = st.file_uploader("Upload hourly curtailment CSV", type=["csv"])
    video_uploaded = st.file_uploader("Upload demo video", type=["mp4", "mov", "m4v", "avi"])

    st.markdown("<div class='sidebar-panel'><div class='sidebar-panel-title'>Default local files detected</div><div class='sidebar-panel-note'>These files were found automatically in the app folder.</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-file-line'><div class='sidebar-file-label'>N-0 workbook</div><div class='sidebar-file-name'>{0}</div></div>".format(DEFAULT_N0_FILE.name if DEFAULT_N0_FILE else "Not found"), unsafe_allow_html=True)
    st.markdown("<div class='sidebar-file-line'><div class='sidebar-file-label'>Generator ZIP</div><div class='sidebar-file-name'>{0}</div></div>".format(DEFAULT_GEN_ZIP.name if DEFAULT_GEN_ZIP else "Not found"), unsafe_allow_html=True)
    st.markdown("<div class='sidebar-file-line'><div class='sidebar-file-label'>Hourly curtailment CSV</div><div class='sidebar-file-name'>{0}</div></div>".format(DEFAULT_GEN_ADJ_FILE.name if DEFAULT_GEN_ADJ_FILE else "Not found"), unsafe_allow_html=True)
    st.markdown("<div class='sidebar-file-line'><div class='sidebar-file-label'>Demo video</div><div class='sidebar-file-name'>{0}</div></div></div>".format(DEFAULT_VIDEO_FILE.name if DEFAULT_VIDEO_FILE else "Not found"), unsafe_allow_html=True)

try:
    n0_bytes = read_file_bytes(n0_uploaded.getvalue() if n0_uploaded is not None else None, DEFAULT_N0_FILE, required=True)
    gen_bytes = read_file_bytes(gen_uploaded.getvalue() if gen_uploaded is not None else None, DEFAULT_GEN_ZIP, required=True)
    total_adj_bytes = read_file_bytes(total_adj_uploaded.getvalue() if total_adj_uploaded is not None else None, DEFAULT_GEN_ADJ_FILE, required=False)
    video_bytes = read_file_bytes(video_uploaded.getvalue() if video_uploaded is not None else None, DEFAULT_VIDEO_FILE, required=False)
except Exception as e:
    st.error("Could not load input files: {0}".format(e))
    st.stop()

try:
    n0_df = load_n0_hourly_table(n0_bytes)
except Exception as e:
    st.error("Could not parse N-0 hourly data: {0}".format(e))
    st.stop()

try:
    generator_names = list_generators_from_zip(gen_bytes)
except Exception as e:
    st.error("Could not parse generator ZIP file: {0}".format(e))
    st.stop()

if not generator_names:
    st.error("No generator CSV files were found inside the ZIP.")
    st.stop()

year = int(n0_df["time"].dt.year.mode().iloc[0])

total_adj_df = None
if total_adj_bytes is not None:
    try:
        total_adj_df = load_total_curtailment_table(total_adj_bytes, year)
    except Exception as e:
        st.warning("Hourly curtailment CSV could not be parsed, so that section is skipped: {0}".format(e))

control_col1, control_col2 = st.columns(2)

with control_col1:
    hour_options = n0_df["hour_no"].tolist()
    selected_hour = st.selectbox(
        "Select hour (1 to 8760)",
        options=hour_options,
        format_func=lambda x: "Hour {0} | {1}".format(x, n0_df.loc[n0_df["hour_no"] == x, "time"].iloc[0]),
    )

with control_col2:
    selected_generator = st.selectbox("Generator curtailment", options=generator_names)

selected_hour_row = n0_df.loc[n0_df["hour_no"] == selected_hour].iloc[0]
selected_gen_df = load_generator_series(gen_bytes, selected_generator, year)
selected_gen_row = selected_gen_df.loc[selected_gen_df["hour_no"] == selected_hour].iloc[0]
selected_total_row = None
if total_adj_df is not None:
    selected_total_row = total_adj_df.loc[total_adj_df["hour_no"] == selected_hour].iloc[0]

insight_cards = [
    render_insight_card(
        "Hour Number",
        str(int(selected_hour)),
        "Selected study hour from the annual 8760-hour timeline.",
        "blue",
    ),
    render_insight_card(
        "Timestamp",
        str(selected_hour_row["time"]).replace(" 00:00:00", "") if pd.notna(selected_hour_row["time"]) else "No data",
        "Calendar timestamp linked to the selected hour.",
        "blue",
    ),
    render_insight_card(
        "Max Loading (%)",
        format_num(selected_hour_row.get("max_loading_pre"), 2),
        "Higher loading means greater congestion stress in the network.",
        insight_class_for_loading(selected_hour_row.get("max_loading_pre")),
    ),
    render_insight_card(
        "Thermal Violations",
        format_int_like(selected_hour_row.get("thermal_viol_pre")),
        "Shows how many thermal limit violations occurred in this hour.",
        insight_class_for_violations(selected_hour_row.get("thermal_viol_pre")),
    ),
    render_insight_card(
        "{0} Curtailment".format(selected_generator),
        format_mw(selected_gen_row.get("GEN_ADJ")),
        "Selected generator curtailment at this exact hour.",
        insight_class_for_curtailment(selected_gen_row.get("GEN_ADJ")),
    ),
    render_insight_card(
        "Total Curtailment",
        "No data" if selected_total_row is None else format_mw(selected_total_row.get("GEN_ADJ_SUM_MW")),
        "System-wide curtailed generation for the selected hour.",
        "blue" if selected_total_row is None else insight_class_for_curtailment(selected_total_row.get("GEN_ADJ_SUM_MW")),
    ),
]

st.markdown(
    """
    <div class='section-box'>
        <div class='insight-heading'>Important insights for the selected hour</div>
        <div class='insight-subtext'>Highlighted results are shown below with shaded cards so the key congestion and curtailment indicators are easier to read.</div>
        <div class='insight-grid'>
            {0}
        </div>
    </div>
    """.format("".join(insight_cards)),
    unsafe_allow_html=True,
)

if not bool(selected_hour_row.get("n0_data_available", False)):
    st.warning("No N-0 result is available for this hour in the Raw_Hourly sheet.")
if not bool(selected_gen_row.get("gen_data_available", False)):
    st.warning("No generator value is available for {0} at this hour in the uploaded ZIP file.".format(selected_generator))
if selected_total_row is not None and not bool(selected_total_row.get("total_curtailment_available", False)):
    st.warning("No total hourly curtailment value is available for this hour in the uploaded CSV.")

summary_tab, gen_tab, total_tab, video_tab, preview_tab = st.tabs([
    "Hour Summary", "Generator View", "Hourly Curtailment View", "Demo Video", "Workbook Preview"
])

with summary_tab:
    left, right = st.columns([1, 1])

    with left:
        st.markdown("### N-0 result for selected hour")
        hour_table = selected_hour_row.to_frame(name="value").reset_index()
        hour_table.columns = ["field", "value"]
        st.dataframe(hour_table, use_container_width=True, hide_index=True)
        st.download_button(
            "Download selected hour result (CSV)",
            data=hour_table.to_csv(index=False).encode("utf-8"),
            file_name="n0_hour_{0}.csv".format(selected_hour),
            mime="text/csv",
        )

    with right:
        st.markdown("### Selected curtailment values for this hour")
        combined_rows = [
            {"field": "hour_no", "value": selected_hour},
            {"field": "timestamp", "value": selected_hour_row.get("time")},
            {"field": "selected_generator", "value": selected_generator},
            {"field": "generator_curtailment_MW", "value": selected_gen_row.get("GEN_ADJ")},
            {"field": "generator_data_available", "value": selected_gen_row.get("gen_data_available")},
        ]
        if selected_total_row is not None:
            combined_rows.extend([
                {"field": "total_curtailment_MW", "value": selected_total_row.get("GEN_ADJ_SUM_MW")},
                {"field": "total_curtailment_available", "value": selected_total_row.get("total_curtailment_available")},
            ])
        combined_hour_table = pd.DataFrame(combined_rows)
        st.dataframe(combined_hour_table, use_container_width=True, hide_index=True)
        st.download_button(
            "Download selected hour curtailment summary (CSV)",
            data=combined_hour_table.to_csv(index=False).encode("utf-8"),
            file_name="selected_hour_curtailment_{0}.csv".format(selected_hour),
            mime="text/csv",
        )

with gen_tab:
    st.markdown("### Selected generator curtailment by hour")
    st.markdown("<div class='small-note'>This section shows the full hourly curtailment trace for the selected generator.</div>", unsafe_allow_html=True)
    gen_plot_df = selected_gen_df[["hour_no", "DateTime", "GEN_ADJ", "gen_data_available"]].copy()
    st.dataframe(gen_plot_df, use_container_width=True, hide_index=True)

    available_gen_plot_df = gen_plot_df[gen_plot_df["gen_data_available"]].copy()
    if not available_gen_plot_df.empty:
        st.line_chart(available_gen_plot_df.set_index("DateTime")[["GEN_ADJ"]])
    else:
        st.info("No plottable generator values were found for the selected generator.")

    st.download_button(
        "Download full selected generator series (CSV)",
        data=gen_plot_df.to_csv(index=False).encode("utf-8"),
        file_name="{0}_full_series.csv".format(selected_generator),
        mime="text/csv",
    )

with total_tab:
    st.markdown("### Hourly curtailment file view")
    st.markdown("<div class='small-note'>This section uses gen_adj_hourly.csv to show total hourly curtailment across the system.</div>", unsafe_allow_html=True)
    if total_adj_df is None:
        st.info("Upload or place gen_adj_hourly.csv in the same folder to show this section.")
    else:
        total_plot_df = total_adj_df[["hour_no", "DateTime", "GEN_ADJ_SUM_MW", "total_curtailment_available"]].copy()
        st.dataframe(total_plot_df, use_container_width=True, hide_index=True)

        available_total_plot_df = total_plot_df[total_plot_df["total_curtailment_available"]].copy()
        if not available_total_plot_df.empty:
            st.line_chart(available_total_plot_df.set_index("DateTime")[["GEN_ADJ_SUM_MW"]])
        else:
            st.info("No plottable total curtailment values were found in the hourly curtailment CSV.")

        if selected_total_row is not None:
            st.markdown("### Selected hour from hourly curtailment file")
            selected_total_table = pd.DataFrame([
                {"field": "hour_no", "value": selected_total_row.get("hour_no")},
                {"field": "DateTime", "value": selected_total_row.get("DateTime")},
                {"field": "GEN_ADJ_SUM_MW", "value": selected_total_row.get("GEN_ADJ_SUM_MW")},
                {"field": "available", "value": selected_total_row.get("total_curtailment_available")},
            ])
            st.dataframe(selected_total_table, use_container_width=True, hide_index=True)

        st.download_button(
            "Download full hourly curtailment series (CSV)",
            data=total_plot_df.to_csv(index=False).encode("utf-8"),
            file_name="hourly_curtailment_full_series.csv",
            mime="text/csv",
        )

with video_tab:
    st.markdown("### Demo video")
    if video_bytes is None:
        st.info("Upload or place Demo_Video.mp4 in the same folder to show the video here.")
    else:
        st.video(video_bytes)
        st.download_button(
            "Download demo video",
            data=video_bytes,
            file_name=DEFAULT_VIDEO_FILE.name if DEFAULT_VIDEO_FILE else "demo_video.mp4",
            mime="video/mp4",
        )

with preview_tab:
    st.markdown("### Optional workbook preview")
    sheet_names = load_excel_sheet_names(n0_bytes)
    preview_sheet = st.selectbox("Preview any sheet from the N-0 workbook", options=sheet_names)
    preview_rows = st.slider("Preview rows", min_value=5, max_value=100, value=20, step=5)
    preview_df = load_sheet_preview(n0_bytes, preview_sheet, nrows=preview_rows)
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

with st.expander("Data quality notes"):
    st.write("N-0 hourly rows found in Raw_Hourly: {0} out of 8760 calendar hours.".format(int(n0_df["n0_data_available"].sum())))
    st.write("Selected generator rows found for {0}: {1} out of 8760 calendar hours.".format(
        selected_generator,
        int(selected_gen_df["gen_data_available"].sum())
    ))
    if total_adj_df is not None:
        st.write("Hourly curtailment rows found: {0} out of 8760 calendar hours.".format(
            int(total_adj_df["total_curtailment_available"].sum())
        ))
    if video_bytes is not None:
        st.write("Demo video loaded successfully.")
