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
# ==========================
# READ EXCEL
# ==========================

if uploaded_file:

    st.sidebar.success("โหลดไฟล์สำเร็จ")

    st.sidebar.write(uploaded_file.name)

    st.sidebar.write(
        datetime.now().strftime("%d/%m/%Y %H:%M")
    )

    with st.spinner("กำลังอ่านข้อมูล..."):

        df1 = get_data(
            uploaded_file,
            "Sheet1",
            "หมายเลขเครื่องจักร"
        )

        df_own = get_data(
            uploaded_file,
            "ซ่อมเอง",
            "หมายเลขเครื่องจักรกล"
        )

        df_comp = get_data(
            uploaded_file,
            "เบ็ดเสร็จ",
            "หมายเลขเครื่องจักรกล"
        )

    if df1 is None:

        st.error("ไม่พบข้อมูล Sheet1")

        st.stop()

    # ==========================
    # SEARCH
    # ==========================

    if search_machine != "":

        result = df1[
            df1["หมายเลขเครื่องจักร"]
            .astype(str)
            .str.contains(
                search_machine,
                case=False,
                na=False
            )
        ]

        if len(result):

            st.success("พบข้อมูล")

            st.dataframe(
                result,
                use_container_width=True
            )

        else:

            st.warning("ไม่พบหมายเลขเครื่องจักร")

    # ==========================
    # KPI
    # ==========================

    repair = df1[
        df1["เครื่องจักรรอซ่อม"]
        .apply(is_valid_machine_id)
    ]

    vacant = df1[
        df1["เครื่องจักรว่าง"]
        .apply(is_valid_machine_id)
    ]

    total = df1["หมายเลขเครื่องจักร"].nunique()

    repair_count = len(repair)

    vacant_count = len(vacant)

    rent_count = total - repair_count - vacant_count

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "เครื่องจักรทั้งหมด",
        total
    )

    c2.metric(
        "เช่าใช้งาน",
        rent_count
    )

    c3.metric(
        "รอซ่อม",
        repair_count
    )

    c4.metric(
        "ว่าง",
        vacant_count
    )

    st.divider()
  
