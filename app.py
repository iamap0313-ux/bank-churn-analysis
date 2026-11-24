import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bank Churn Dashboard", layout="wide")
df = pd.read_csv("European_Bank_clean.csv")
overall_all = df["Exited"].mean() * 100          # bank-wide churn rate, used as the benchmark

st.title("European Bank: Customer Churn Dashboard")
st.caption("Use the filters on the left. Every number and chart updates with them.")


# ---------- small helpers ----------
def rate(d):
    """Churn rate (%) of a table of customers."""
    return d["Exited"].mean() * 100


def show_bar(series, title):
    """Draw one bar chart from a Series of churn rates (keeps the order we give it)."""
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.bar(series.index.astype(str), series.values, color="#4c72b0")
    ax.set_title(title, fontsize=10)
    ax.set_ylabel("Churn rate (%)")
    for i, v in enumerate(series.values):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def churn_series(data, column, order=None):
    s = data.groupby(column)["Exited"].mean() * 100
    if order:
        s = s.reindex([o for o in order if o in s.index])
    return s


# ---------- sidebar filters (segment filters) ----------
st.sidebar.header("Segment filters")


def pick(label, column):
    options = sorted(df[column].unique())
    return st.sidebar.multiselect(label, options, default=options)


geo = pick("Country", "Geography")
gender = pick("Gender", "Gender")
age = pick("Age band", "AgeBand")
credit = pick("Credit band", "CreditBand")
tenure = pick("Tenure group", "TenureGroup")
balance = pick("Balance segment", "BalanceSegment")

f = df[df["Geography"].isin(geo) & df["Gender"].isin(gender) & df["AgeBand"].isin(age)
       & df["CreditBand"].isin(credit) & df["TenureGroup"].isin(tenure)
       & df["BalanceSegment"].isin(balance)]

if f.empty:
    st.warning("No customers match these filters. Widen the filters on the left.")
    st.stop()

# ---------- the five KPIs ----------
hv = f[f["BalanceSegment"] == "High"]
geo_rate = f.groupby("Geography")["Exited"].mean() * 100
act = f.groupby("IsActiveMember")["Exited"].mean() * 100
inactive, active = act.get(0, float("nan")), act.get(1, float("nan"))

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Overall churn rate", f"{rate(f):.1f}%", f"{len(f):,} customers", delta_color="off")
k2.metric("High-value churn ratio", f"{rate(hv):.1f}%" if len(hv) else "n/a")
k3.metric("Geographic risk index", f"{geo_rate.max() / overall_all * 100:.0f}",
          f"highest: {geo_rate.idxmax()}", delta_color="off")
k4.metric("Inactive members churn", f"{inactive:.1f}%")
k5.metric("Active members churn", f"{active:.1f}%")
st.caption("Geographic risk index: 100 = bank average. Segment churn rates are in the tabs below.")

# ---------- four modules ----------
tab1, tab2, tab3, tab4 = st.tabs(["Overall summary", "Geography", "Age and tenure", "High-value customers"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        show_bar(churn_series(f, "Gender"), "Churn rate by gender (%)")
    with c2:
        show_bar(churn_series(f, "IsActiveMember"), "Churn rate: 0 = inactive, 1 = active (%)")
    c3, c4 = st.columns(2)
    with c3:
        show_bar(churn_series(f, "NumOfProducts"), "Churn rate by number of products (%)")
    with c4:
        show_bar(churn_series(f, "CreditBand", ["Low", "Medium", "High"]), "Churn rate by credit band (%)")

with tab2:
    g = f.groupby("Geography")["Exited"].agg(customers="size", churned="sum", churn_rate="mean")
    g["churn_rate"] = (g["churn_rate"] * 100).round(1)
    g["risk_index"] = (g["churn_rate"] / overall_all * 100).round(0)
    g["share_of_churners_%"] = (g["churned"] / g["churned"].sum() * 100).round(1)
    left, right = st.columns([1, 1])
    with left:
        show_bar(g["churn_rate"], "Churn rate by country (%)")
    with right:
        st.subheader("Country table")
        st.dataframe(g, use_container_width=True)
    st.subheader("Country by age band: churn rate (%)")
    grid = pd.crosstab(f["Geography"], f["AgeBand"], values=f["Exited"], aggfunc="mean") * 100
    grid = grid.reindex(columns=[a for a in ["<30", "30-45", "46-60", "60+"] if a in grid.columns])
    st.dataframe(grid.round(1), use_container_width=True)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        show_bar(churn_series(f, "AgeBand", ["<30", "30-45", "46-60", "60+"]), "Churn rate by age band (%)")
    with c2:
        show_bar(churn_series(f, "TenureGroup", ["New", "Mid-term", "Long-term"]), "Churn rate by tenure group (%)")
    st.subheader("Churned vs retained: average profile")
    prof = f.groupby("Exited")[["Age", "CreditScore", "Balance", "EstimatedSalary", "Tenure"]].mean().round(1)
    prof.index = prof.index.map({0: "Retained", 1: "Churned"})
    st.dataframe(prof, use_container_width=True)

with tab4:
    st.subheader("High-value customer explorer")
    threshold = st.slider("High-value means balance above", 0, int(df["Balance"].max()), 100000, step=10000)
    hvx = f[f["Balance"] > threshold]
    if hvx.empty:
        st.info("No customers have a balance above this level. Lower the slider.")
    else:
        m1, m2, m3 = st.columns(3)
        lost = hvx.loc[hvx["Exited"] == 1, "Balance"].sum()
        m1.metric("Customers above threshold", f"{len(hvx):,}")
        m2.metric("Churn rate", f"{rate(hvx):.1f}%")
        m3.metric("Balance lost to churn", f"{lost:,.0f}", f"{lost / f['Balance'].sum() * 100:.1f}% of all balance", delta_color="off")
        st.subheader("Churned vs retained: salary and balance")
        cmp_ = hvx.groupby("Exited")[["EstimatedSalary", "Balance", "Age", "CreditScore"]].mean().round(0)
        cmp_.index = cmp_.index.map({0: "Retained", 1: "Churned"})
        st.dataframe(cmp_, use_container_width=True)
        st.subheader("Drill-down: highest-balance customers who left")
        cols = ["CustomerId", "Geography", "Gender", "Age", "Balance", "EstimatedSalary", "NumOfProducts", "IsActiveMember"]
        st.dataframe(hvx[hvx["Exited"] == 1].sort_values("Balance", ascending=False)[cols].head(50),
                     use_container_width=True, hide_index=True)
