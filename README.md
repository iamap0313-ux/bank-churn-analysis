# European Bank: Customer Churn Analysis

Unified Mentor internship project by Alpesh Patel.

## What this project does

Customer churn means a customer leaves the bank. This project looks at 10,000 customers (France, Germany, Spain) and finds which groups leave the most, by country, gender, age, credit score, tenure and balance, and how much money is at risk. A Streamlit dashboard lets you filter the segments and see the numbers update.

## Dashboard

- **Overall summary**: churn by gender, activity, number of products and credit band
- **Geography**: churn by country, a country table with a risk index, and country by age band
- **Age and tenure**: churn by age band and tenure group, and a churned vs retained profile
- **High-value customers**: a slider to define "high balance", with churn rate, balance lost and the biggest customers who left

## Files

| File | Purpose |
|---|---|
| `app.py` | The Streamlit dashboard |
| `European_Bank_clean.csv` | Cleaned data with the segment columns added |
| `requirements.txt` | Python libraries needed |

## How to run

```
pip install -r requirements.txt
python -m streamlit run app.py
```

## Definitions and assumptions

The segment cut points are my own choices, because the brief only names the bands.

- Age band: under 30, 30 to 45, 46 to 60, over 60
- Credit band: Low below 600, Medium 600 to 700, High above 700
- Tenure group: New 0 to 2 years, Mid-term 3 to 6, Long-term 7 to 10
- Balance segment: Zero, Low up to 100,000, High above 100,000
- Geographic risk index: a country's churn rate divided by the overall churn rate, times 100 (100 means average)

This data shows which groups leave, not why. Results describe associations, not causes.
