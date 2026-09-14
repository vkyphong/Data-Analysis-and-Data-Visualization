"""
==============================================================
 PHAN TICH MO TA VA CHAN DOAN - 6 BIEU DO
 De tai: Cai thien ty le dung gio cua Delta Air Lines
 Thuc hien: Nguyen Minh Quan
 Nguon du lieu: Kaggle usdot/flight-delays (2015), loc rieng Delta Air Lines
==============================================================
Cau hoi nghien cuu:
"Cac yeu to ve thoi gian, san bay khoi hanh, tuyen bay va nguyen nhan van
hanh anh huong nhu the nao den tinh trang tre chuyen cua Delta Air Lines,
va Delta nen uu tien cai thien o dau de nang cao ty le dung gio truoc mua
cao diem?"

Input:  flights_DL.csv, airlines.csv
Output: 6 file bieu do (.png)
        key_findings.csv
        recommendation_evidence.csv
        6 bang so lieu trung gian (airport/monthly/route/hour/delay_cause/month_severity)
==============================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLIGHTS_PATH = os.path.join(BASE_DIR, "flights_DL.csv")  # da loc rieng Delta Air Lines (DL)
AIRLINES_PATH = os.path.join(BASE_DIR, "airlines.csv")

sns.set_style("whitegrid")

# Nguong toi thieu de 1 tuyen duoc xet la "high-risk route", tranh truong
# hop tuyen chi bay vai chuyen nhung ty le tre 100% khong co y nghia thong ke.
MIN_FLIGHTS = 500

# Nguong toi thieu de 1 san bay khoi hanh duoc xem la san bay co san luong
# khai thac lon cua Delta (khong dung tu "hub" vi day khong phai dinh nghia
# hub chinh thuc theo mang bay hub-and-spoke, chi la nguong loc thong ke).
AIRPORT_MIN_FLIGHTS = 1000
TOP_N_AIRPORTS = 15


# ==============================================================
# 1. LOAD DU LIEU VA XAC DINH ANALYTICAL POPULATION
# ==============================================================
usecols = [
    "MONTH", "DAY_OF_WEEK", "AIRLINE",
    "ORIGIN_AIRPORT_CLEAN", "DEST_AIRPORT_CLEAN",
    "SCHEDULED_DEPARTURE", "DISTANCE", "DIVERTED", "CANCELLED",
    "ARRIVAL_DELAY", "IS_DELAYED",
    "AIR_SYSTEM_DELAY", "SECURITY_DELAY", "AIRLINE_DELAY",
    "LATE_AIRCRAFT_DELAY", "WEATHER_DELAY",
]

dtype_map = {
    "MONTH": "int8", "DAY_OF_WEEK": "int8", "AIRLINE": "category",
    "ORIGIN_AIRPORT_CLEAN": "category", "DEST_AIRPORT_CLEAN": "category",
    "SCHEDULED_DEPARTURE": "float32", "DISTANCE": "int32",
    "DIVERTED": "int8", "CANCELLED": "int8",
    "ARRIVAL_DELAY": "float32", "IS_DELAYED": "float32",
    "AIR_SYSTEM_DELAY": "float32", "SECURITY_DELAY": "float32",
    "AIRLINE_DELAY": "float32", "LATE_AIRCRAFT_DELAY": "float32",
    "WEATHER_DELAY": "float32",
}

print("[1] Doc du lieu tu flights_DL.csv...")
df = pd.read_csv(FLIGHTS_PATH, usecols=usecols, dtype=dtype_map)
print(f"    {df.shape[0]:,} dong, {df.shape[1]} cot.")

airlines = pd.read_csv(AIRLINES_PATH).rename(columns={"AIRLINE": "AIRLINE_NAME"})
df = df.merge(airlines, left_on="AIRLINE", right_on="IATA_CODE", how="left")

# IS_DELAYED duoc tinh truc tiep tu ARRIVAL_DELAY trong buoc lam sach du lieu:
# = 1 neu ARRIVAL_DELAY >= 15 phut (chuan US DOT), = 0 neu < 15 phut,
# = khong xac dinh neu khong co ARRIVAL_DELAY. Cac quan sat khong xac dinh
# tu dong bi loai khoi moi phep tinh ty le vi ham .mean() cua pandas bo qua
# gia tri rong.

print("[1b] Doi chieu IS_DELAYED voi ARRIVAL_DELAY >= 15:")
print(pd.crosstab(df["IS_DELAYED"], df["ARRIVAL_DELAY"] >= 15))

# Analytical population: chi xet chuyen KHONG bi chuyen huong, KHONG bi huy,
# va co gia tri ARRIVAL_DELAY. Loc tuong minh ca 3 dieu kien (thay vi chi
# dua vao IS_DELAYED tu dong bo qua NaN) de de kiem chung va doi chieu.
n_before = df.shape[0]
n_diverted = int((df["DIVERTED"] == 1).sum())
n_cancelled = int((df["CANCELLED"] == 1).sum())
df = df[
    (df["DIVERTED"] == 0) &
    (df["CANCELLED"] == 0) &
    (df["ARRIVAL_DELAY"].notna())
].copy()
print(f"[1c] Loai {n_diverted:,} chuyen bi chuyen huong va {n_cancelled:,} chuyen "
      f"bi huy khoi {n_before:,} dong; con lai {df.shape[0]:,} dong.")

overall_rate = df["IS_DELAYED"].mean() * 100
n_eligible = int(df["IS_DELAYED"].notna().sum())
n_delayed = int(df["IS_DELAYED"].sum())
print(f"[2] Trong {n_eligible:,} chuyen du dieu kien, {n_delayed:,} chuyen tre "
      f">= 15 phut, tuong duong {overall_rate:.1f}%.")


# ==============================================================
# PHAN MO TA (DESCRIPTIVE) - 3 BIEU DO
# Trinh tu: Tong quan -> San bay nao -> Tuyen nao
# ==============================================================

# --- Bieu do 1: Ty le dung gio theo thang (Line chart) ---
monthly = df.groupby("MONTH")["IS_DELAYED"].mean().reset_index()
monthly["ON_TIME_RATE"] = (1 - monthly["IS_DELAYED"]) * 100

plt.figure(figsize=(9, 5.5))
plt.plot(monthly["MONTH"], monthly["ON_TIME_RATE"], marker="o", color="steelblue",
          linewidth=2, markersize=7)
for x, y in zip(monthly["MONTH"], monthly["ON_TIME_RATE"]):
    plt.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 10),
                 ha="center", fontsize=9)
plt.title("Tỷ lệ đúng giờ của Delta Air Lines theo tháng (2015)")
plt.xlabel("Tháng")
plt.ylabel("Tỷ lệ đúng giờ (%)")
plt.xticks(range(1, 13))
plt.ylim(70, 100)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "chart1_ontime_theo_thang.png"), dpi=150)
plt.close()
print("[3] Da luu chart1_ontime_theo_thang.png")

# --- Bieu do 2: Ty le tre theo san bay khoi hanh cua Delta (Bar chart) ---
# Doi tu "theo hang" sang "theo san bay khoi hanh" vi du lieu gio chi con 1
# hang (Delta), so sanh giua cac hang khong con y nghia. Khong dung tu "hub"
# vi day chi la nguong loc thong ke, khong phai dinh nghia hub chinh thuc.
airport_summary = df.dropna(subset=["IS_DELAYED"]).groupby("ORIGIN_AIRPORT_CLEAN", observed=True).agg(
    total_flights=("IS_DELAYED", "size"),
    delay_rate=("IS_DELAYED", "mean"),
)
airport_summary["delay_rate"] *= 100
airport_eligible = airport_summary[airport_summary["total_flights"] >= AIRPORT_MIN_FLIGHTS]
print(f"[4c] {len(airport_summary)} san bay khoi hanh tong cong, {len(airport_eligible)} san bay dat "
      f"nguong >= {AIRPORT_MIN_FLIGHTS} chuyen (san bay co san luong khai thac lon).")

airport_rate = airport_eligible["delay_rate"].sort_values(ascending=False).head(TOP_N_AIRPORTS)

plt.figure(figsize=(10, 6))
airport_rate.plot(kind="bar", color="indianred")
plt.axhline(overall_rate, color="black", linestyle="--",
            label=f"Trung bình toàn bộ Delta ({overall_rate:.1f}%)")
plt.title(f"Tỷ lệ trễ theo sân bay khởi hành — Top {len(airport_rate)} sân bay sản lượng cao của Delta")
plt.xlabel("Sân bay khởi hành (mã IATA)")
plt.ylabel("Tỷ lệ trễ (%)")
plt.legend()
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "chart2_tre_theo_san_bay.png"), dpi=150)
plt.close()
print("[4] Da luu chart2_tre_theo_san_bay.png")


# --- Bieu do 3: Route Risk - khoi luong vs ty le tre (Scatter chart) ---
df["ROUTE"] = df["ORIGIN_AIRPORT_CLEAN"].astype(str) + " - " + df["DEST_AIRPORT_CLEAN"].astype(str)

# Loai cac chuyen co ma san bay khong hop le (nhan "UNKNOWN" tu buoc lam sach)
# khoi phan tich tuyen bay, vi day khong phai 1 tuyen thuc te ma la tap hop
# nhieu ma san bay la bi gom chung, gay outlier khi ve bieu do.
n_before_route = df.shape[0]
df_route = df[
    (df["ORIGIN_AIRPORT_CLEAN"] != "UNKNOWN") & (df["DEST_AIRPORT_CLEAN"] != "UNKNOWN")
]
n_unknown = n_before_route - df_route.shape[0]
print(f"[4a] Loai {n_unknown:,} chuyen co ma san bay khong hop le "
      f"({n_unknown/n_before_route*100:.2f}% tong so) khoi phan tich tuyen bay.")

route_summary = df_route.dropna(subset=["IS_DELAYED"]).groupby("ROUTE").agg(
    total_flights=("IS_DELAYED", "size"),
    delayed_flights=("IS_DELAYED", "sum"),
    delay_rate=("IS_DELAYED", "mean"),
)
route_summary["delay_rate"] *= 100
route_summary_eligible = route_summary[route_summary["total_flights"] >= MIN_FLIGHTS].copy()
print(f"[4b] {len(route_summary)} tuyen tong cong, {len(route_summary_eligible)} tuyen dat "
      f"nguong >= {MIN_FLIGHTS} chuyen.")

top_routes_risk = route_summary_eligible.sort_values("delay_rate", ascending=False).head(10)
route_delay = top_routes_risk["delay_rate"]
route_summary_eligible["IS_TOP10"] = route_summary_eligible.index.isin(top_routes_risk.index)

normal_pts = route_summary_eligible[~route_summary_eligible["IS_TOP10"]]
top_pts = route_summary_eligible[route_summary_eligible["IS_TOP10"]]

plt.figure(figsize=(10, 7))
plt.scatter(normal_pts["total_flights"], normal_pts["delay_rate"],
            s=30, alpha=0.35, color="steelblue", label=f"Tuyến đạt ngưỡng (n={len(normal_pts)})")
plt.scatter(top_pts["total_flights"], top_pts["delay_rate"],
            s=80, alpha=0.9, color="crimson", label="Top 10 rủi ro cao nhất")

top_sorted = top_pts.sort_values("delay_rate", ascending=False)
label_x = route_summary_eligible["total_flights"].quantile(0.90)
y_positions = np.linspace(top_sorted["delay_rate"].max() + 1, top_sorted["delay_rate"].min() - 1, len(top_sorted))
for (route_name, row), y_label in zip(top_sorted.iterrows(), y_positions):
    plt.annotate(
        route_name,
        xy=(row["total_flights"], row["delay_rate"]),
        xytext=(label_x, y_label),
        fontsize=8,
        arrowprops=dict(arrowstyle="-", color="gray", lw=0.6, alpha=0.7),
        va="center",
    )
plt.axhline(overall_rate, color="black", linestyle="--", linewidth=1,
            label=f"Trung bình toàn bộ Delta ({overall_rate:.1f}%)")
plt.title(f"Rủi ro theo tuyến bay của Delta: số chuyến so với tỷ lệ trễ (tuyến ≥ {MIN_FLIGHTS} chuyến)")
plt.xlabel("Tổng số chuyến bay (khối lượng khai thác)")
plt.ylabel("Tỷ lệ trễ (%)")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "chart3_route_risk_scatter.png"), dpi=150)
plt.close()
print("[5] Da luu chart3_route_risk_scatter.png")
print(top_routes_risk)

# Kiem chung noi bo: total_flights phai bang dung delayed + ontime, va
# delay_rate tinh lai tu delayed_flights/total_flights phai khop tuyet doi.
route_summary["ontime_flights"] = route_summary["total_flights"] - route_summary["delayed_flights"]
assert (route_summary["total_flights"] ==
        route_summary["delayed_flights"] + route_summary["ontime_flights"]).all()
route_summary["check_rate"] = route_summary["delayed_flights"] / route_summary["total_flights"] * 100
max_diff = (route_summary["delay_rate"] - route_summary["check_rate"]).abs().max()
print(f"[5b] Kiem chung route: sai lech delay_rate lon nhat = {max_diff:.10f}")


# ==============================================================
# PHAN CHAN DOAN (DIAGNOSTIC) - 3 BIEU DO
# Trinh tu: Nguyen nhan gi -> Khi nao -> Nghiem trong the nao
# ==============================================================

# --- Bieu do 4: Ty trong nguyen nhan tre (Pie chart) ---
reason_cols = ["AIR_SYSTEM_DELAY", "SECURITY_DELAY", "AIRLINE_DELAY", "LATE_AIRCRAFT_DELAY", "WEATHER_DELAY"]
reason_label = {
    "AIR_SYSTEM_DELAY": "   Hệ thống không lưu quốc gia",
    "SECURITY_DELAY": "An ninh",
    "AIRLINE_DELAY": "Hãng hàng không",
    "LATE_AIRCRAFT_DELAY": "Máy bay đến trễ chuyến trước",
    "WEATHER_DELAY": "Thời tiết",
}
reason_totals = df.loc[df["IS_DELAYED"] == 1, reason_cols].sum()
reason_pct = reason_totals / reason_totals.sum() * 100
reason_pct.index = [reason_label[c] for c in reason_pct.index]

plt.figure(figsize=(7, 7))
plt.pie(reason_pct, labels=reason_pct.index, autopct="%1.1f%%", startangle=90,
        colors=sns.color_palette("Set2"))
plt.title("Tỷ trọng nguyên nhân gây trễ chuyến của Delta (theo tổng phút trễ)")
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "chart4_nguyennhan_tre.png"), dpi=150)
plt.close()
print("[6] Da luu chart4_nguyennhan_tre.png")

# --- Bieu do 5: Ty le tre theo gio khoi hanh x ngay trong tuan (Heatmap) ---
def extract_hour(x):
    try:
        return int(x) // 100
    except (ValueError, TypeError):
        return np.nan

df["SCHED_HOUR"] = df["SCHEDULED_DEPARTURE"].apply(extract_hour)
pivot = df.pivot_table(index="SCHED_HOUR", columns="DAY_OF_WEEK", values="IS_DELAYED", aggfunc="mean") * 100
count_pivot = df.pivot_table(index="SCHED_HOUR", columns="DAY_OF_WEEK", values="IS_DELAYED", aggfunc="count")

plt.figure(figsize=(12, 10))
ax = sns.heatmap(pivot, cmap="YlOrRd", cbar_kws={"label": "Tỷ lệ trễ (%)"}, annot=False)
vmin, vmax = pivot.values.min(), pivot.values.max()
threshold = vmin + (vmax - vmin) * 0.6
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        value = pivot.values[i, j]
        text_color = "white" if value >= threshold else "black"
        ax.text(j + 0.5, i + 0.5, f"{value:.1f}", ha="center", va="center",
                 color=text_color, fontsize=13)
plt.title("Tỷ lệ trễ của Delta theo giờ khởi hành và ngày trong tuần")
plt.xlabel("Ngày trong tuần (1 = Thứ 2 ... 7 = Chủ nhật)")
plt.ylabel("Giờ khởi hành theo lịch (0-23h)")
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "chart5_heatmap_gio_ngay.png"), dpi=150)
plt.close()
print("[7] Da luu chart5_heatmap_gio_ngay.png")

low_sample_cells = int((count_pivot < 50).sum().sum())
print(f"[7a] So o co duoi 50 chuyen quan sat trong ma tran gio x ngay: {low_sample_cells}.")
count_pivot.to_csv(os.path.join(BASE_DIR, "heatmap_hour_dow_count.csv"))

# hour_summary: ty le tre GOP theo tung gio (dung so chuyen tre / tong so
# chuyen du dieu kien tai gio do), KHAC voi pivot.mean(axis=1) (la trung
# binh don gian cua 7 ty le theo ngay, khong theo trong so so chuyen thuc
# te tung ngay). Dung hour_summary de xac dinh F7 cho chinh xac.
hour_summary = (
    df.dropna(subset=["IS_DELAYED"])
    .groupby("SCHED_HOUR", observed=True)
    .agg(
        total_flights=("IS_DELAYED", "size"),
        delayed_flights=("IS_DELAYED", "sum"),
        delay_rate=("IS_DELAYED", "mean"),
    )
)
hour_summary["delay_rate"] *= 100
hour_summary.to_csv(os.path.join(BASE_DIR, "hour_delay_summary.csv"))
print("[7c] Ty le tre gop theo gio khoi hanh (hour_summary):")
print(hour_summary)

# Cross analysis: heatmap chi cho thay ty le tre tang dan trong ngay, khong
# tu no chung minh nguyen nhan la tre day chuyen. Kiem tra rieng bang trung
# binh phut LATE_AIRCRAFT_DELAY theo gio khoi hanh.
late_aircraft_by_hour = (
    df[df["IS_DELAYED"] == 1]
    .groupby("SCHED_HOUR")["LATE_AIRCRAFT_DELAY"]
    .mean()
)
print("[7b] Trung binh phut LATE_AIRCRAFT_DELAY theo gio khoi hanh (chuyen bi tre):")
print(late_aircraft_by_hour)

# --- Bieu do 6: Phan bo phut tre theo thang (Boxplot) ---
# Bo tro truc tiep cho Bieu do 1 (Line chart theo thang): Bieu do 1 tra loi
# "thang nao tre NHIEU LAN" (tan suat), Bieu do 6 tra loi "thang nao tre NANG"
# (muc do nghiem trong khi da tre). Dung thang thay vi san bay de khong lap
# truc voi Bieu do 2 (da la "theo san bay" roi).
delayed = df[df["IS_DELAYED"] == 1]

plt.figure(figsize=(10, 6))
sns.boxplot(data=delayed, x="MONTH", y="ARRIVAL_DELAY", showfliers=False,
            hue="MONTH", palette="pastel", legend=False)
plt.title("Phân bố ARRIVAL_DELAY của Delta theo tháng (chỉ chuyến đã trễ ≥ 15 phút)")
plt.xlabel("Tháng")
plt.ylabel("Phút trễ")
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "chart6_boxplot_tre_theo_thang.png"), dpi=150)
plt.close()
print("[8] Da luu chart6_boxplot_tre_theo_thang.png")

median_delay_by_month = delayed.groupby("MONTH")["ARRIVAL_DELAY"].median().sort_values()
print("[8b] Median phut tre theo thang (chuyen bi tre), thap den cao:")
print(median_delay_by_month)


# ==============================================================
# TONG HOP KEY FINDINGS VA CAC BANG SO LIEU DAU RA
# ==============================================================
worst_month_row = monthly.loc[monthly["ON_TIME_RATE"].idxmin()]
best_month_row = monthly.loc[monthly["ON_TIME_RATE"].idxmax()]
worst_airport = airport_rate.index[0]
worst_route = route_delay.index[0] if len(route_delay) else "N/A"
worst_route_rate = route_delay.iloc[0] if len(route_delay) else float("nan")
worst_route_n = int(top_routes_risk["total_flights"].iloc[0]) if len(top_routes_risk) else 0
main_reason = reason_pct.idxmax()
worst_hour_row = hour_summary.loc[hour_summary["delay_rate"].idxmax()]
worst_hour = int(worst_hour_row.name)
worst_hour_rate = float(worst_hour_row["delay_rate"])
worst_severity_month = int(median_delay_by_month.index[-1])
worst_severity_value = median_delay_by_month.iloc[-1]

key_findings = pd.DataFrame([
    {"ID": "F1", "Dimension": "Overall", "Finding": "Ty le tre chung toan bo Delta Air Lines",
     "Value": f"{overall_rate:.1f}%"},
    {"ID": "F2", "Dimension": "Season", "Finding": f"Thang co ty le dung gio thap nhat: thang {int(worst_month_row['MONTH'])}",
     "Value": f"{worst_month_row['ON_TIME_RATE']:.1f}% dung gio"},
    {"ID": "F3", "Dimension": "Season", "Finding": f"Thang co ty le dung gio cao nhat: thang {int(best_month_row['MONTH'])}",
     "Value": f"{best_month_row['ON_TIME_RATE']:.1f}% dung gio"},
    {"ID": "F4", "Dimension": "Airport", "Finding": f"San bay khoi hanh co ty le tre cao nhat: {worst_airport}",
     "Value": f"{airport_rate.max():.1f}% (cao hon TB {airport_rate.max()-overall_rate:.1f} diem %)"},
    {"ID": "F5", "Dimension": "Route", "Finding": f"Tuyen rui ro cao nhat (>= {MIN_FLIGHTS} chuyen): {worst_route}",
     "Value": f"{worst_route_rate:.1f}% tren {worst_route_n:,} chuyen"},
    {"ID": "F6", "Dimension": "Cause", "Finding": f"Nguyen nhan tre chiem ty trong lon nhat: {main_reason}",
     "Value": f"{reason_pct.max():.1f}% tong phut tre"},
    {"ID": "F7", "Dimension": "Time", "Finding": f"Khung gio co ty le tre cao nhat: {worst_hour}h",
     "Value": f"{worst_hour_rate:.1f}%"},
    {"ID": "F8", "Dimension": "Severity", "Finding": f"Thang co muc do tre nghiem trong nhat (median phut tre): thang {worst_severity_month}",
     "Value": f"{worst_severity_value:.0f} phut"},
])

print("\n" + "=" * 70)
print("KEY FINDINGS")
print("=" * 70)
print(key_findings.to_string(index=False))
print("=" * 70)

key_findings.to_csv(os.path.join(BASE_DIR, "key_findings.csv"), index=False)

# Bang so lieu ho tro cho phan Chi dinh (Prescriptive Analysis)
recommendation_evidence = pd.DataFrame([
    {"Finding": "Airport", "Metric": "Delay Rate", "Value": f"{airport_rate.max():.1f}%",
     "Implication": f"San bay {worst_airport} can duoc uu tien ra soat nguyen nhan van hanh"},
    {"Finding": "Peak Hour", "Metric": "Delay Rate", "Value": f"{worst_hour_rate:.1f}%",
     "Implication": f"Nen tang buffer thoi gian / bo tri may bay du phong vao khung {worst_hour}h"},
    {"Finding": "Route", "Metric": "Delay Rate",
     "Value": f"{worst_route_rate:.1f}% tren {worst_route_n:,} chuyen",
     "Implication": f"Uu tien nguon luc du phong cho tuyen {worst_route}"},
    {"Finding": "Cause", "Metric": "Share of Delay Minutes", "Value": f"{reason_pct.max():.1f}%",
     "Implication": "Van de chinh nam o van hanh/xoay vong may bay, can cai thien lich trinh quay dau"},
    {"Finding": "Season", "Metric": "On-time Rate",
     "Value": f"Thang {int(worst_month_row['MONTH'])}: {worst_month_row['ON_TIME_RATE']:.1f}%",
     "Implication": "Can chuan bi nguon luc du phong truoc mua cao diem (he)"},
    {"Finding": "Severity", "Metric": "Median Arrival Delay",
     "Value": f"Thang {worst_severity_month}: {worst_severity_value:.0f} phut",
     "Implication": "Ngoai tan suat, can chu y thang co muc do tre nghiem trong hon khi len ke hoach du phong"},
])
recommendation_evidence.to_csv(os.path.join(BASE_DIR, "recommendation_evidence.csv"), index=False)

airport_summary.to_csv(os.path.join(BASE_DIR, "airport_delay_summary.csv"))
monthly.to_csv(os.path.join(BASE_DIR, "monthly_delay_summary.csv"), index=False)
route_summary_eligible.to_csv(os.path.join(BASE_DIR, "route_delay_summary.csv"))
reason_pct.to_csv(os.path.join(BASE_DIR, "delay_cause_summary.csv"))
median_delay_by_month.to_csv(os.path.join(BASE_DIR, "month_severity_summary.csv"))

print("\nDa xuat: key_findings.csv, recommendation_evidence.csv, "
      "airport/monthly/route/hour/delay_cause/month_severity_summary.csv")