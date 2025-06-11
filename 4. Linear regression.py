import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ——— Constants —————————————————————————————————————————————————————————————————
DATA_PATH = '/data/FIC_LIWC_filtered_date_10190.csv'
CATEGORIES = ['Affect', 'Cognition', 'Perception']

# ——— 1. Load & clean data —————————————————————————————————————————————————————
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=['year'])                    # remove rows missing a year
df['year'] = df['year'].astype(int)                # ensure integer years
df['decade'] = (df['year'] // 10) * 10             # bucket into decades

# ——— 2. Compute mean LIWC scores by decade —————————————————————————————————————
decade_mean = (
    df
    .groupby('decade')[CATEGORIES]
    .mean()
    .reset_index()
)

# ——— 3. Fit OLS for each category & build APA‐style table ——————————————————————
rows = []
for cat in CATEGORIES:
    # Prepare predictors and outcome
    X = sm.add_constant(decade_mean['decade'])
    y = decade_mean[cat]
    
    # Fit model
    model = sm.OLS(y, X).fit()
    
    # Extract stats
    b      = model.params['decade']
    se     = model.bse['decade']
    ci_low, ci_high = model.conf_int().loc['decade']
    t_val  = model.tvalues['decade']
    p_val  = model.pvalues['decade']
    r2     = model.rsquared
    f_val  = model.fvalue
    df_m, df_r = int(model.df_model), int(model.df_resid)
    
    # Format p‐value string
    p_str = '< .001' if p_val < 0.001 else f'= {p_val:.3f}'
    
    # Append to results
    rows.append({
        'DV':       cat,
        'b':        round(b, 5),
        'SE':       round(se, 5),
        '95% CI':   f"[{ci_low:.5f}, {ci_high:.5f}]",
        't':        round(t_val, 2),
        'p':        p_str,
        'R²':       round(r2, 3),
        'F':        round(f_val, 2),
        'df':       f"({df_m}, {df_r})"
    })

# Create and display the table
apa_table = pd.DataFrame(rows, 
    columns=['DV','b','SE','95% CI','t','p','R²','F','df']
)
print("Regression Results:\n", apa_table.to_string(index=False))


# ——— 4. Plotting function ——————————————————————————————————————————————————————
def plot_trend(decades, scores, category):
    """
    Scatter + OLS fit with 95% CI ribbon for one LIWC category across decades.
    """
    mask = scores.notna()
    x = decades[mask].astype(float)
    y = scores[mask].astype(float)
    
    # Re‐fit model on the filtered data
    X = sm.add_constant(x)
    model = sm.OLS(y, X).fit()
    pred  = model.get_prediction(X).summary_frame(alpha=0.05)
    
    # Format p‐value for title
    p_val = model.pvalues['decade']
    p_str = '< .001' if p_val < 0.001 else f'= {p_val:.3f}'
    
    # Build the plot
    fig, ax = plt.subplots()
    ax.scatter(x, y, marker='x', label='Mean score')
    ax.plot(x, pred['mean'],       label='OLS fit')
    ax.fill_between(
        x, 
        pred['mean_ci_lower'], 
        pred['mean_ci_upper'], 
        alpha=0.2, 
        label='95% CI'
    )
    ax.set_title(f"{category} by Decade (R\u00b2={model.rsquared:.2f}, p {p_str})")
    ax.set_xlabel("Decade")
    ax.set_ylabel(category)
    ax.legend()
    plt.tight_layout()
    plt.show()


# ——— 5. Generate plots for each category —————————————————————————————————————
for cat in CATEGORIES:
    plot_trend(decade_mean['decade'], decade_mean[cat], cat)
