
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="BSC TTĐHTT", layout="wide")

# ========== ĐỌC DANH SÁCH NHÂN VIÊN TỪ FILE EXCEL ==========
@st.cache_data
def load_danh_sach_nhan_vien():
    try:
        df_nv = pd.read_excel("T7_Mẫu_Giao KH BSC Cá nhân T7.2025 - ĐHTT.xlsx", sheet_name=0)
        df_nv = df_nv[["Tổ công tác", "Họ và tên"]].dropna()
        return df_nv
    except:
        return pd.DataFrame({"Tổ công tác": [], "Họ và tên": []})

ds_nv_df = load_danh_sach_nhan_vien()
to_list = sorted(ds_nv_df["Tổ công tác"].unique())

# ========== NHẬP DỮ LIỆU ==========
st.title("📊 Tính điểm BSC - TTĐHTT VNPT Yên Bái")

col1, col2 = st.columns(2)
with col1:
    thang = st.date_input("🗓️ Tháng", datetime.date.today())
    to_cong_tac = st.selectbox("🧭 Tổ công tác", to_list)
    nhan_vien_ds = ds_nv_df[ds_nv_df["Tổ công tác"] == to_cong_tac]["Họ và tên"].tolist()
    ho_ten = st.selectbox("👤 Họ và tên", nhan_vien_ds)
with col2:
    bts = st.number_input("⛔ BTS (phút)", 0.0)
    nodeb = st.number_input("🔗 NodeB (phút)", 0.0)
    enodeb = st.number_input("🌐 eNodeB (phút)", 0.0)
    sc1 = st.number_input("🚨 SC mức 1", 0)
    sc2 = st.number_input("⚠️ SC mức 2", 0)
    sc3 = st.number_input("⚠️ SC mức 3", 0)

# ========== TÍNH TOÁN ==========
def tinh_diem(bts, nodeb, enodeb, sc1, sc2, sc3):
    diem = 100
    diem -= bts * 0.1
    diem -= nodeb * 0.05
    diem -= enodeb * 0.05
    diem -= sc1 * 5
    diem -= sc2 * 2
    diem -= sc3 * 1
    return round(max(diem, 0), 2)

data_bsc = []

if st.button("✅ Tính điểm BSC"):
    diem_bsc = tinh_diem(bts, nodeb, enodeb, sc1, sc2, sc3)
    st.success(f"🎯 Điểm BSC: {diem_bsc} điểm")

    new_data = {
        "Tháng": thang.strftime("%Y-%m"),
        "Tổ": to_cong_tac,
        "Họ tên": ho_ten,
        "BTS": bts,
        "NodeB": nodeb,
        "eNodeB": enodeb,
        "SC1": sc1,
        "SC2": sc2,
        "SC3": sc3,
        "Điểm BSC": diem_bsc
    }
    st.session_state.setdefault("data_bsc", []).append(new_data)

# ========== HIỂN THỊ KẾT QUẢ ==========
if "data_bsc" in st.session_state and st.session_state["data_bsc"]:
    df_kq = pd.DataFrame(st.session_state["data_bsc"])
    st.subheader("📋 Bảng kết quả chi tiết")
    st.dataframe(df_kq)

    df_tb_to = df_kq.groupby(["Tháng", "Tổ"])["Điểm BSC"].mean().reset_index(name="TB tổ")
    df_tb_donvi = df_kq.groupby("Tháng")["Điểm BSC"].mean().reset_index(name="TB đơn vị")

    st.subheader("📊 Biểu đồ điểm trung bình")
    fig, ax = plt.subplots()
    for to in df_tb_to["Tổ"].unique():
        df_plot = df_tb_to[df_tb_to["Tổ"] == to]
        ax.plot(df_plot["Tháng"], df_plot["TB tổ"], marker='o', label=to)
    ax.plot(df_tb_donvi["Tháng"], df_tb_donvi["TB đơn vị"], linestyle='--', marker='s', label="Toàn đơn vị", color="black")
    ax.set_ylabel("Điểm")
    ax.set_xlabel("Tháng")
    ax.set_title("Biểu đồ điểm trung bình theo tổ và toàn đơn vị")
    ax.legend()
    st.pyplot(fig)

    # Xuất file Excel
    def convert_df():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_kq.to_excel(writer, index=False, sheet_name="ChiTiet")
            df_tb_to.to_excel(writer, index=False, sheet_name="TB_Theo_To")
            df_tb_donvi.to_excel(writer, index=False, sheet_name="TB_Don_Vi")
        return output.getvalue()

    st.download_button(
        "📥 Tải file kết quả",
        data=convert_df(),
        file_name="BSC_TTĐHTT_KetQua.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ========== CHỨC NĂNG TƯƠNG LAI ==========
st.markdown("🔧 **Sắp có**: Nhập liệu từ Google Sheet (gắn tự động)")
