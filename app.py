import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(layout="wide", page_title="Executive Dashboard - ส่วนเครื่องกล")

def is_valid_machine_id(val):
    if pd.isna(val):
        return False
    pattern = r'^\d{2}-\d{4}-\d{2}-\d$'
    return bool(re.match(pattern, str(val).strip()))

def get_data(file, sheet, anchor):
    try:
        df_raw = pd.read_excel(file, sheet_name=sheet, header=None)

        for i, row in df_raw.iterrows():
            if anchor in row.values:
                df = pd.read_excel(file, sheet_name=sheet, header=i)
                return df.dropna(how='all')

    except Exception:
        return None

    return None

st.title("📊 Executive Dashboard: ส่วนเครื่องกล")

uploaded_file = st.file_uploader(
    "อัปโหลดไฟล์ Excel ประจำเดือน",
    type=["xlsx"]
)

if uploaded_file:

    st.sidebar.info(f"ไฟล์ปัจจุบัน: {uploaded_file.name}")
    st.sidebar.write(
        f"อัปเดตล่าสุด: {datetime.now().strftime('%d %B %Y เวลา %H:%M น.')}"
    )

    with st.spinner("กำลังประมวลผลข้อมูล..."):

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

    if df1 is not None and df_own is not None and df_comp is not None:

        repair_list = df1[
            df1["เครื่องจักรรอซ่อม"].apply(is_valid_machine_id)
        ]

        vacant_list = df1[
            df1["เครื่องจักรว่าง"].apply(is_valid_machine_id)
        ]

        total = df1["หมายเลขเครื่องจักร"].nunique()
        repair_count = len(repair_list)
        vacant_count = len(vacant_list)
        rent_count = total - repair_count - vacant_count

        with st.expander("🔍 ตรวจสอบความถูกต้อง (Data Validation)"):

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            c1.metric("เครื่องจักรทั้งหมด", total)
            c2.metric("เช่าใช้งาน", rent_count)
            c3.metric("รอซ่อม", repair_count)
            c4.metric("ว่าง", vacant_count)
            c5.metric("ซ่อมเอง", len(df_own))
            c6.metric("เบ็ดเสร็จ", len(df_comp))

        tab1, tab2 = st.tabs(
            ["หน้า 1: ภาพรวมเครื่องจักร", "หน้า 2: งานซ่อมบำรุง"]
        )

        with tab1:

            st.header("ภาพรวมสถานะเครื่องจักร")

            k1, k2, k3, k4 = st.columns(4)

            k1.metric("เครื่องจักรทั้งหมด", total)
            k2.metric("เช่าใช้งาน", rent_count)
            k3.metric("รอซ่อม", repair_count)
            k4.metric("ว่าง", vacant_count)

            if "หน่วยงานที่เช่าใช้" in df1.columns:
                st.bar_chart(
                    df1.groupby("หน่วยงานที่เช่าใช้")["หมายเลขเครื่องจักร"].count()
                )

        with tab2:

            st.header("ผลการดำเนินงานซ่อมบำรุง")

            left, right = st.columns(2)

            with left:

                st.subheader("ซ่อมเอง")

                st.metric(
                    "งานทั้งหมด",
                    len(df_own)
                )

                st.metric(
                    "ตรวจรับแล้ว",
                    df_own["วันที่ตรวจรับ"].notna().sum()
                )

            with right:

                st.subheader("เบ็ดเสร็จ")

                st.metric(
                    "งานทั้งหมด",
                    len(df_comp)
                )

                st.metric(
                    "ตรวจรับแล้ว",
                    df_comp["วันที่ตรวจรับ"].notna().sum()
                )

    else:
        st.error("⚠️ ไม่พบข้อมูลที่จำเป็น โปรดตรวจสอบชื่อ Sheet และหัวคอลัมน์")

else:
    st.info("กรุณาอัปโหลดไฟล์ Excel เพื่อเริ่มใช้งาน Dashboard")
