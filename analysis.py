"""
Marketing Analytics Dashboard
==============================
Combines Social Media Sentiment + E-Commerce Sales data
to deliver brand health, platform performance, and revenue insights.

Datasets:
  - sentimentdataset.csv  (732 real social media posts)
  - ecommerce_10000.csv   (10,000 real e-commerce orders)

Author : [Your Name]
Tools  : Python · Pandas · Matplotlib · Seaborn
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Seaborn theme ────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.05)
PALETTE = {"Positive": "#2ECC71", "Negative": "#E74C3C", "Neutral": "#95A5A6"}

# ════════════════════════════════════════════════════════════
# 1.  LOAD & CLEAN DATA
# ════════════════════════════════════════════════════════════

# ── Sentiment ────────────────────────────────────────────────
sent = pd.read_csv("sentimentdataset.csv")
sent.columns = sent.columns.str.strip()
sent["Sentiment"] = sent["Sentiment"].str.strip()
sent["Platform"]  = sent["Platform"].str.strip()
sent["Country"]   = sent["Country"].str.strip()

# Normalise to 3 core sentiments
pos_words = {"Positive","Happiness","Joy","Love","Happy","Relief","Excited"}
neg_words = {"Negative","Anger","Fear","Sadness","Disgust","Hate","Bad","Sad","Embarrassed"}
def normalise(s):
    if s in pos_words: return "Positive"
    if s in neg_words: return "Negative"
    return "Neutral"

sent["CoreSentiment"] = sent["Sentiment"].apply(normalise)
sent["Timestamp"] = pd.to_datetime(sent["Timestamp"], errors="coerce")
sent["Month"] = sent["Timestamp"].dt.month

# ── E-Commerce ───────────────────────────────────────────────
eco = pd.read_csv("ecommerce_10000.csv")
eco.columns = eco.columns.str.strip()
eco["OrderDate"] = pd.to_datetime(eco["OrderDate"], errors="coerce")
eco["Month"] = eco["OrderDate"].dt.month
eco["MonthName"] = eco["OrderDate"].dt.strftime("%b")

print("=" * 58)
print("   MARKETING ANALYTICS DASHBOARD — DATA SUMMARY")
print("=" * 58)
print(f"\n📱 Social posts loaded  : {len(sent):,}")
print(f"🛒 E-commerce orders   : {len(eco):,}")
print(f"   Brands (ecommerce)  : {eco['Brand'].nunique()}")
print(f"   Categories          : {', '.join(eco['Category'].unique())}")
print(f"   Platforms           : {', '.join(eco['Platform'].unique())}")

# ── Quick stats ──────────────────────────────────────────────
print("\n📊 Overall Sentiment:")
for s, n in sent["CoreSentiment"].value_counts().items():
    pct = n / len(sent) * 100
    print(f"   {s:10s}: {n:>3}  ({pct:.1f}%)")

print("\n💰 Top 5 Brands by Revenue:")
top_brands = eco.groupby("Brand")["TotalAmount"].sum().sort_values(ascending=False).head(5)
for brand, rev in top_brands.items():
    print(f"   {brand:12s}: ${rev:>12,.0f}")

# ════════════════════════════════════════════════════════════
# 2.  BUILD DASHBOARD  (3 rows × 3 cols)
# ════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(18, 14))
fig.suptitle("Marketing Analytics Dashboard\nSocial Sentiment + E-Commerce Performance",
             fontsize=18, fontweight="bold", y=1.01)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

# ─── ROW 1 ──────────────────────────────────────────────────

# Chart 1-1: Overall Sentiment Donut
ax1 = fig.add_subplot(gs[0, 0])
counts = sent["CoreSentiment"].value_counts()
wedge_colors = [PALETTE[s] for s in counts.index]
wedges, _, autotexts = ax1.pie(
    counts.values, labels=counts.index, autopct="%1.1f%%",
    colors=wedge_colors, startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 2},
    pctdistance=0.78
)
# donut hole
centre = plt.Circle((0, 0), 0.55, fc="white")
ax1.add_patch(centre)
ax1.text(0, 0, f"{len(sent)}\nposts", ha="center", va="center",
         fontsize=10, fontweight="bold", color="#333")
for at in autotexts:
    at.set_fontsize(9); at.set_fontweight("bold")
ax1.set_title("Overall Social Sentiment", fontweight="bold")

# Chart 1-2: Sentiment by Platform
ax2 = fig.add_subplot(gs[0, 1])
plat_sent = sent.groupby(["Platform", "CoreSentiment"]).size().unstack(fill_value=0)
plat_sent = plat_sent.reindex(columns=["Positive", "Neutral", "Negative"])
x = range(len(plat_sent))
width = 0.25
for i, (sentiment, color) in enumerate(PALETTE.items()):
    vals = plat_sent.get(sentiment, pd.Series([0]*len(plat_sent))).values
    ax2.bar([xi + i*width for xi in x], vals, width=width,
            label=sentiment, color=color, edgecolor="white")
ax2.set_xticks([xi + width for xi in x])
ax2.set_xticklabels(plat_sent.index)
ax2.set_title("Sentiment by Platform", fontweight="bold")
ax2.set_ylabel("Posts")
ax2.legend(fontsize=8)

# Chart 1-3: Top Countries by Post Volume
ax3 = fig.add_subplot(gs[0, 2])
top_countries = sent["Country"].value_counts().head(8)
bars = ax3.barh(top_countries.index[::-1], top_countries.values[::-1],
                color=sns.color_palette("Blues_d", len(top_countries)),
                edgecolor="white")
for bar, val in zip(bars, top_countries.values[::-1]):
    ax3.text(val + 0.5, bar.get_y() + bar.get_height()/2,
             str(val), va="center", fontsize=9)
ax3.set_title("Posts by Country", fontweight="bold")
ax3.set_xlabel("Number of Posts")

# ─── ROW 2 ──────────────────────────────────────────────────

# Chart 2-1: Monthly Revenue Trend
ax4 = fig.add_subplot(gs[1, :2])
monthly_rev = eco.groupby(["Month","MonthName"])["TotalAmount"].sum().reset_index()
monthly_rev = monthly_rev.sort_values("Month")
ax4.fill_between(monthly_rev["MonthName"], monthly_rev["TotalAmount"],
                 alpha=0.25, color="#3498DB")
ax4.plot(monthly_rev["MonthName"], monthly_rev["TotalAmount"],
         marker="o", color="#2980B9", linewidth=2.5, markersize=7)
for _, row in monthly_rev.iterrows():
    ax4.text(row["MonthName"], row["TotalAmount"] * 1.015,
             f"${row['TotalAmount']/1e6:.1f}M",
             ha="center", fontsize=8, color="#2980B9", fontweight="bold")
ax4.set_title("Monthly Revenue Trend", fontweight="bold")
ax4.set_ylabel("Total Revenue ($)")
ax4.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax4.tick_params(axis="x", rotation=30)

# Chart 2-2: Revenue by Category (pie)
ax5 = fig.add_subplot(gs[1, 2])
cat_rev = eco.groupby("Category")["TotalAmount"].sum().sort_values(ascending=False)
cat_colors = sns.color_palette("Set2", len(cat_rev))
ax5.pie(cat_rev.values, labels=cat_rev.index, autopct="%1.0f%%",
        colors=cat_colors, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 8})
ax5.set_title("Revenue by Category", fontweight="bold")

# ─── ROW 3 ──────────────────────────────────────────────────

# Chart 3-1: Top 10 Brands by Revenue
ax6 = fig.add_subplot(gs[2, :2])
top10 = eco.groupby("Brand")["TotalAmount"].sum().sort_values(ascending=False).head(10)
bar_colors = sns.color_palette("RdYlGn_r", 10)
bars = ax6.bar(top10.index, top10.values, color=bar_colors, edgecolor="white", width=0.6)
for bar, val in zip(bars, top10.values):
    ax6.text(bar.get_x() + bar.get_width()/2, val * 1.01,
             f"${val/1e6:.1f}M", ha="center", fontsize=8, fontweight="bold")
ax6.set_title("Top 10 Brands by Total Revenue", fontweight="bold")
ax6.set_ylabel("Revenue ($)")
ax6.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax6.tick_params(axis="x", rotation=35)

# Chart 3-2: Avg Rating by Platform
ax7 = fig.add_subplot(gs[2, 2])
plat_rating = eco.groupby("Platform")["Rating"].mean().sort_values(ascending=False)
colors_r = ["#2ECC71" if r >= 3 else "#E74C3C" for r in plat_rating.values]
bars = ax7.bar(plat_rating.index, plat_rating.values,
               color=colors_r, edgecolor="white", width=0.5)
ax7.axhline(3, color="gray", linestyle="--", linewidth=1, alpha=0.7)
for bar, val in zip(bars, plat_rating.values):
    ax7.text(bar.get_x() + bar.get_width()/2, val + 0.05,
             f"{val:.2f}", ha="center", fontsize=11, fontweight="bold")
ax7.set_title("Avg Customer Rating\nby E-Commerce Platform", fontweight="bold")
ax7.set_ylabel("Rating (out of 5)")
ax7.set_ylim(0, 5.5)

# ════════════════════════════════════════════════════════════
# 3.  SAVE
# ════════════════════════════════════════════════════════════

plt.savefig("marketing_dashboard.png", dpi=150, bbox_inches="tight")
print("\n✅ Dashboard saved → marketing_dashboard.png")

# ── Bonus: export summary CSVs ───────────────────────────────
sent[["Timestamp","Text","Platform","Country","CoreSentiment","Likes","Retweets"]]\
    .to_csv("sentiment_clean.csv", index=False)
eco.groupby(["Brand","Category"])["TotalAmount"].sum()\
    .reset_index().sort_values("TotalAmount", ascending=False)\
    .to_csv("brand_revenue_summary.csv", index=False)

print("✅ sentiment_clean.csv exported")
print("✅ brand_revenue_summary.csv exported")
print("\n🎉 All done!")
