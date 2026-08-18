import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(
    page_title="Executive Dashboard - ส่วนเครื่องกล",
    page_icon="🏛️",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    background: linear-gradient(90deg,#0B5CAD,#1976D2);
    padding: 24px;
    border-radius: 14px;
    text-align: center;
    color: white;
}
</style>
<div class="main-title">
<h2>🏛️ กรมทางหลวง</h2>
<h3>สำนักงานทางหลวงที่ 17</h3>
<h3>ส่วนเครื่องกล</h3>
<h1>Executive Dashboard</h1>
</div>
""", unsafe_allow_html=True)

MACHINE_PATTERN = re.compile(r"^\d{2}-\d{4}-\d{2}-\d$")

def is_valid_machine_id(value):
    if pd.isna(value):
        return False
    return bool(MACHINE_PATTERN.match(str(value).strip()))

def read_sheet(file, sheet_name, anchor):
    try:
        raw = pd.read_excel(file, sheet_name=sheet_name, header=None)
    except Exception:
        return None

    header_row = None
    for i, row in raw.iterrows():
        if anchor in row.astype(str).str.strip().tolist():
            header_row = i
            break

    if header_row is None:
        return None

    try:
        df = pd.read_excel(
            file,
            sheet_name=sheet_name,
            header=header_row
        ).dropna(how="all")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        return None

def received_count(df):
    if df is None or "วันที่ตรวจรับ" not in df.columns:
        return 0
    return int(df["วันที่ตรวจรับ"].notna().sum())

uploaded_file = st.file_uploader(
    "📂 อัปโหลดไฟล์ Excel ประจำเดือน",
    type=["xlsx"]
)

search_machine = st.text_input(
    "🔎 ค้นหาหมายเลขเครื่องจักร",
    placeholder="เช่น 41-0001-01-1"
)

if not uploaded_file:
    st.info("📂 กรุณาอัปโหลดไฟล์ Excel เพื่อเริ่มใช้งาน Dashboard")
    st.stop()

st.sidebar.success("โหลดไฟล์สำเร็จ")
st.sidebar.write(f"ไฟล์: {uploaded_file.name}")
st.sidebar.write(
    datetime.now().strftime("อ่านข้อมูลเมื่อ %d/%m/%Y %H:%M น.")
)

with st.spinner("กำลังอ่านข้อมูลจาก Excel..."):
    df1 = read_sheet(uploaded_file, "Sheet1", "หมายเลขเครื่องจักร")
    df_own = read_sheet(uploaded_file, "ซ่อมเอง", "หมายเลขเครื่องจักรกล")
    df_comp = read_sheet(uploaded_file, "เบ็ดเสร็จ", "หมายเลขเครื่องจักรกล")

if df1 is None:
    st.error(
        "❌ ไม่สามารถอ่าน Sheet1 ได้ กรุณาตรวจสอบชื่อ Sheet "
        "และหัวคอลัมน์ 'หมายเลขเครื่องจักร'"
    )
    st.stop()

if df_own is None:
    df_own = pd.DataFrame()
if df_comp is None:
    df_comp = pd.DataFrame()

if "หมายเลขเครื่องจักร" not in df1.columns:
    st.error("❌ Sheet1 ไม่มีคอลัมน์ 'หมายเลขเครื่องจักร'")
    st.stop()

if search_machine.strip():
    result = df1[
        df1["หมายเลขเครื่องจักร"].astype(str).str.contains(
            search_machine.strip(),
            case=False,
            na=False,
            regex=False
        )
    ]
    if len(result):
        st.success(f"พบข้อมูล {len(result)} รายการ")
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("ไม่พบหมายเลขเครื่องจักรนี้")

if "เครื่องจักรรอซ่อม" in df1.columns:
    repair = df1[
        df1["เครื่องจักรรอซ่อม"].apply(is_valid_machine_id)
    ]
    repair_count = int(
        repair["เครื่องจักรรอซ่อม"].nunique()
    )
else:
    repair_count = 0

if "เครื่องจักรว่าง" in df1.columns:
    vacant = df1[
        df1["เครื่องจักรว่าง"].apply(is_valid_machine_id)
    ]
    vacant_count = int(
        vacant["เครื่องจักรว่าง"].nunique()
    )
else:
    vacant_count = 0

total = int(
    df1["หมายเลขเครื่องจักร"]
    .dropna()
    .astype(str)
    .str.strip()
    .nunique()
)

rent_count = max(total - repair_count - vacant_count, 0)

st.subheader("📌 สรุปภาพรวม")
k1, k2, k3, k4 = st.columns(4)
k1.metric("เครื่องจักรทั้งหมด", total)
k2.metric("เช่าใช้งาน", rent_count)
k3.metric("รอซ่อม", repair_count)
k4.metric("ว่าง", vacant_count)

st.divider()

tab1, tab2 = st.tabs([
    "📊 หน้า 1: ภาพรวมเครื่องจักร",
    "🔧 หน้า 2: งานซ่อมบำรุง"
])

with tab1:
    st.subheader("📊 ภาพรวมสถานะเครื่องจักร")

    if "หน่วยงานที่เช่าใช้" in df1.columns:
        chart = (
            df1.assign(
                หน่วยงานที่เช่าใช้=df1["หน่วยงานที่เช่าใช้"]
                .fillna("ไม่ระบุ")
                .astype(str)
                .str.strip()
            )
            .groupby("หน่วยงานที่เช่าใช้")["หมายเลขเครื่องจักร"]
            .count()
            .sort_values(ascending=False)
        )
        if len(chart):
            st.markdown("### จำนวนเครื่องจักรตามหน่วยงานที่เช่าใช้")
            st.bar_chart(chart)

    st.markdown("### รายละเอียดเครื่องจักร")
    display_df = df1.copy()

    if search_machine.strip():
        display_df = display_df[
            display_df["หมายเลขเครื่องจักร"].astype(str).str.contains(
                search_machine.strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=520
    )

with tab2:
    st.subheader("🔧 ผลการดำเนินงานซ่อมบำรุง")
    left, right = st.columns(2)

    with left:
        st.markdown("### 🔧 ซ่อมเอง")
        own_total = len(df_own)
        own_received = received_count(df_own)
        own_not_received = max(own_total - own_received, 0)

        a, b, c = st.columns(3)
        a.metric("งานทั้งหมด", own_total)
        b.metric("ตรวจรับแล้ว", own_received)
        c.metric("ยังไม่ตรวจรับ", own_not_received)

        if own_total:
            st.dataframe(df_own, use_container_width=True, height=450)
        else:
            st.info("ไม่พบรายการซ่อมเอง")

    with right:
        st.markdown("### 🏭 เบ็ดเสร็จ")
        comp_total = len(df_comp)
        comp_received = received_count(df_comp)
        comp_not_received = max(comp_total - comp_received, 0)

        a, b, c = st.columns(3)
        a.metric("งานทั้งหมด", comp_total)
        b.metric("ตรวจรับแล้ว", comp_received)
        c.metric("ยังไม่ตรวจรับ", comp_not_received)

        if comp_total:
            st.dataframe(df_comp, use_container_width=True, height=450)
        else:
            st.info("ไม่พบรายการเบ็ดเสร็จ")

with st.expander("🔍 ตรวจสอบความถูกต้องของข้อมูล"):
    a, b, c, d, e, f = st.columns(6)
    a.metric("เครื่องจักรทั้งหมด", total)
    b.metric("เช่าใช้งาน", rent_count)
    c.metric("รอซ่อม", repair_count)
    d.metric("ว่าง", vacant_count)
    e.metric("ซ่อมเอง", len(df_own))
    f.metric("เบ็ดเสร็จ", len(df_comp))

    st.write("คอลัมน์ที่อ่านได้จาก Sheet1:")
    st.write(list(df1.columns))
  
