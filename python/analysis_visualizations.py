"""
Food Delivery Marketplace — Business Analysis & Visualizations
Dataset: Food Delivery Cost and Profitability (Kaggle - Apache 2.0)
Author: Harshkumar Nilesh Patel

This script generates all visualizations for the business case study.
Install requirements: pip install pandas matplotlib seaborn numpy
Dataset: https://www.kaggle.com/datasets/romanniki/food-delivery-cost-and-profitability
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Style Config ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
PALETTE   = ["#2E86AB", "#E84855", "#3BB273", "#F5A623", "#7B61FF", "#FF6B35"]
FIG_DIR   = "../visualizations"
os.makedirs(FIG_DIR, exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("../data/food_orders.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("/", "_")

# Parse dates
df["order_date"]    = pd.to_datetime(df["order_date_and_time"])
df["delivery_date"] = pd.to_datetime(df["delivery_date_and_time"])
df["order_month"]   = df["order_date"].dt.to_period("M").astype(str)

# Contribution Margin
df["contribution_margin"] = (
    df["commission_fee"] + df["delivery_fee"]
    - df["payment_processing_fee"]
    - df["discounts_and_offers"]
    - df["refunds_chargebacks"]
)
df["profitable"] = df["contribution_margin"].apply(
    lambda x: "Profitable" if x > 0 else "Loss-Making"
)

# Discount Band
def discount_band(d):
    if d == 0:   return "No Discount"
    if d <= 5:   return "Low (1-5)"
    if d <= 15:  return "Mid (6-15)"
    return "High (15+)"
df["discount_band"] = df["discounts_and_offers"].apply(discount_band)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1: Average Order Value by Payment Method (Horizontal Bar Chart)
# ══════════════════════════════════════════════════════════════════════════════
aov_pay = df.groupby("payment_method").agg(
    avg_order_value=("order_value","mean"),
    total_orders=("order_id","count")
).reset_index().sort_values("avg_order_value", ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(aov_pay["payment_method"], aov_pay["avg_order_value"],
               color=PALETTE[:len(aov_pay)], edgecolor="white", height=0.5)
for bar in bars:
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"${bar.get_width():.2f}", va="center", fontsize=11, fontweight="bold")
ax.set_xlabel("Average Order Value (USD)", fontsize=12)
ax.set_title("Average Order Value by Payment Method", fontsize=14, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/aov_by_payment_method.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 1 saved")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2: Monthly GMV & Order Volume Trend (Dual-Axis Line Chart)
# ══════════════════════════════════════════════════════════════════════════════
monthly = df.groupby("order_month").agg(
    total_orders=("order_id","count"),
    total_gmv=("order_value","sum")
).reset_index().sort_values("order_month")

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()
ax1.bar(monthly["order_month"], monthly["total_orders"],
        color="#2E86AB", alpha=0.7, label="Order Volume", width=0.6)
ax2.plot(monthly["order_month"], monthly["total_gmv"],
         color="#E84855", linewidth=2.5, marker="o", markersize=6, label="GMV (USD)")
ax1.set_xlabel("Month", fontsize=12)
ax1.set_ylabel("Order Volume", color="#2E86AB", fontsize=12)
ax2.set_ylabel("Total GMV (USD)", color="#E84855", fontsize=12)
ax1.set_title("Monthly Order Volume & GMV Trend", fontsize=14, fontweight="bold", pad=15)
plt.xticks(rotation=45, ha="right")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/monthly_gmv_trend.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 2 saved")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3: Profitable vs Loss-Making Orders — Pie + Bar
# ══════════════════════════════════════════════════════════════════════════════
profit_summary = df.groupby("profitable").agg(
    order_count=("order_id","count"),
    total_margin=("contribution_margin","sum"),
    avg_order_value=("order_value","mean")
).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
# Pie
axes[0].pie(profit_summary["order_count"],
            labels=profit_summary["profitable"],
            colors=["#3BB273","#E84855"],
            autopct="%1.1f%%", startangle=140,
            textprops={"fontsize":12, "fontweight":"bold"})
axes[0].set_title("Order Profitability Split", fontsize=13, fontweight="bold")
# Bar - Total Contribution by segment
colors_bar = ["#3BB273" if p == "Profitable" else "#E84855"
              for p in profit_summary["profitable"]]
axes[1].bar(profit_summary["profitable"], profit_summary["total_margin"],
            color=colors_bar, width=0.5, edgecolor="white")
for i, (_, row) in enumerate(profit_summary.iterrows()):
    axes[1].text(i, row["total_margin"] + (50 if row["total_margin"] > 0 else -150),
                 f"${row['total_margin']:,.0f}",
                 ha="center", fontsize=11, fontweight="bold")
axes[1].set_title("Total Contribution Margin by Category", fontsize=13, fontweight="bold")
axes[1].set_ylabel("USD", fontsize=12)
axes[1].yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
plt.suptitle("Profitability Breakdown — 3-Sided Marketplace",
             fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/profitability_breakdown.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 3 saved")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4: Discount Band Impact on Contribution Margin (Grouped Bar)
# ══════════════════════════════════════════════════════════════════════════════
disc_impact = df.groupby("discount_band").agg(
    avg_order_value=("order_value","mean"),
    avg_contribution=("contribution_margin","mean"),
    order_count=("order_id","count")
).reset_index()
order_map = {"No Discount":0, "Low (1-5)":1, "Mid (6-15)":2, "High (15+)":3}
disc_impact["sort"] = disc_impact["discount_band"].map(order_map)
disc_impact = disc_impact.sort_values("sort")

x = np.arange(len(disc_impact))
width = 0.38
fig, ax = plt.subplots(figsize=(11, 5))
bars1 = ax.bar(x - width/2, disc_impact["avg_order_value"],  width,
               label="Avg Order Value",     color="#2E86AB", alpha=0.85)
bars2 = ax.bar(x + width/2, disc_impact["avg_contribution"], width,
               label="Avg Contribution Margin", color="#E84855", alpha=0.85)
for bar in list(bars1) + list(bars2):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f"${bar.get_height():.1f}", ha="center", va="bottom", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(disc_impact["discount_band"], fontsize=11)
ax.set_ylabel("USD (Average)", fontsize=12)
ax.set_title("Discount Impact on Order Value & Contribution Margin",
             fontsize=14, fontweight="bold", pad=15)
ax.legend(fontsize=11)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/discount_impact_margin.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 4 saved")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 5: Delivery Fee as % of Order Value by Order Band (Bar Chart)
# ══════════════════════════════════════════════════════════════════════════════
def order_band(v):
    if v < 15:  return "Low (< $15)"
    if v < 30:  return "Mid ($15-30)"
    if v < 50:  return "High ($30-50)"
    return "Premium (> $50)"
df["order_band"] = df["order_value"].apply(order_band)
band_order = ["Low (< $15)", "Mid ($15-30)", "High ($30-50)", "Premium (> $50)"]
band_data = df.groupby("order_band").agg(
    delivery_fee_pct=("delivery_fee", lambda x:
        (x / df.loc[x.index, "order_value"]).mean() * 100),
    avg_margin=("contribution_margin","mean"),
    count=("order_id","count")
).reindex(band_order).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()
bars = ax1.bar(band_data["order_band"], band_data["delivery_fee_pct"],
               color=PALETTE[:4], alpha=0.85, width=0.5)
ax2.plot(band_data["order_band"], band_data["avg_margin"],
         color="#222222", linewidth=2.5, marker="D", markersize=8,
         label="Avg Contribution Margin", zorder=5)
for bar in bars:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f"{bar.get_height():.1f}%", ha="center", fontsize=10, fontweight="bold")
ax1.set_xlabel("Order Value Band", fontsize=12)
ax1.set_ylabel("Delivery Fee as % of Order Value", color="#555555", fontsize=12)
ax2.set_ylabel("Avg Contribution Margin (USD)", color="#222222", fontsize=12)
ax1.set_title("Delivery Cost-to-Serve by Order Value Band",
              fontsize=14, fontweight="bold", pad=15)
ax2.axhline(0, color="red", linewidth=1, linestyle="--", alpha=0.5)
ax2.legend(loc="upper right", fontsize=10)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.1f"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/delivery_cost_by_order_band.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 5 saved")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 6: Top 10 Restaurants by Refund Rate (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════════
rest_refund = df.groupby("restaurant_id").agg(
    total_orders=("order_id","count"),
    refund_orders=("refunds_chargebacks", lambda x: (x > 0).sum()),
    total_refund=("refunds_chargebacks","sum")
)
rest_refund["refund_rate"] = rest_refund["refund_orders"] / rest_refund["total_orders"] * 100
top_refund = rest_refund[rest_refund["total_orders"] >= 5].nlargest(10, "refund_rate").reset_index()

fig, ax = plt.subplots(figsize=(11, 6))
colors_ref = [PALETTE[1] if r > 20 else PALETTE[0] for r in top_refund["refund_rate"]]
bars = ax.barh(top_refund["restaurant_id"].astype(str),
               top_refund["refund_rate"], color=colors_ref, height=0.6)
ax.axvline(top_refund["refund_rate"].mean(), color="black",
           linestyle="--", linewidth=1.5, label=f"Avg Refund Rate: {top_refund['refund_rate'].mean():.1f}%")
for bar in bars:
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{bar.get_width():.1f}%", va="center", fontsize=10)
ax.set_xlabel("Refund Rate (%)", fontsize=12)
ax.set_title("Top 10 Restaurants by Refund Rate\n(Customer Experience Risk Indicator)",
             fontsize=13, fontweight="bold", pad=15)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/refund_rate_by_restaurant.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 6 saved")

print("\n🎉 All 6 visualizations saved to /visualizations/")
