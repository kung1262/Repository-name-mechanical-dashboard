import streamlit as st
import pandas as pd
import re
from datetime import datetime

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="🏛",
    layout="wide"
)

# ==========================
# HEADER
# ==========================
st.markdown("""
<div style="
background:linear-gradient(90deg,#0B5CAD,#1976D2);
padding:25px;
border-radius:15px;
text-align:center;
color:white;
">

<h2>🏛 กรมทางหลวง</h2>
<h3>สำนักงานทางหลวงที่ 17</h3>
<h3>ส่วนเครื่องกล</h3>

<h1>Executive Dashboard</h1>

</div>
""", unsafe_allow_html=True)

st.write("")

# ==========================
# FUNCTIONS
# ==========================

def is_valid_machine_id(value):

    if pd.isna(value):
        return False

    pattern = r'^\d{2}-\d{4}-\d{2}-\d$'

    return bool(
        re.match(pattern, str(value).strip())
    )


def get_data(file, sheet_name, anchor):

    try:

        raw = pd.read_excel(
            file,
            sheet_name=sheet_name,
            header=None
        )

        for i, row in raw.iterrows():

            if anchor in row.values:

                df = pd.read_excel(
                    file,
                    sheet_name=sheet_name,
                    header=i
                )

                return df.dropna(how="all")

    except:

        return None

    return None


# ==========================
# UPLOAD
# ==========================

uploaded_file = st.file_uploader(
    "📂 อัปโหลดไฟล์ Excel",
    type=["xlsx"]
)

# ==========================
# SEARCH
# ==========================

search_machine = st.text_input(
    "🔎 ค้นหาหมายเลขเครื่องจักร",
    placeholder="เช่น 41-0001-01-1"
)

st.divider()
