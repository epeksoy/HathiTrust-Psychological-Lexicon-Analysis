import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
!pip install statsmodels
# ——— Constants —————————————————————————————————————————————————————————————————
DATA_PATH     = 'data/FIC_LIWC_filtered_date_10190.csv'
CATEGORIES    = ['Affect', 'Cognition', 'Perception']
LOWESS_FRAC   = 0.25
COLORS        = {'Affect': 'red', 'Cognition': 'goldenrod', 'Perception': 'teal'}
FIGURE_PATH   = '/data/Figure_4_trends.png'

GENRE_LABELS  = [
    "Sentimental Novel\nRomanticism\nMoral Realism",
    "Realism\nPsychological Novel",
    "Modernism\nStream-of-\nConsciousness",
    "Noir/Detective\nPostwar Realism",
    "Postmodernism\nAutofiction\nSensory Realism\nProcedural Thriller"
]
GENRE_YEARS   = [1815, 1875, 1920, 1962, 2005]
GENRE_Y_POS   = [97, 87, 68, 87, 97]   # vertical positions for labels

# ——— 1. Load & Prepare Data ——————————————————————————————————————————————————
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=['year'])                   # remove missing years
df['year']   = df['year'].astype(int)             # ensure integer type
df['decade'] = (df['year'] // 10) * 10            # bucket into decades

# ——— 2. Compute Mean LIWC Scores per Decade ————————————————————————————————
decade_mean = (
    df
    .groupby('decade')[CATEGORIES]
    .mean()
    .reset_index()
)

# ——— 3. Min–Max Normalize to 0–100 ————————————————————————————————————————
norm_df = decade_mean.copy()
for cat in CATEGORIES:
    col_min, col_max = norm_df[cat].min(), norm_df[cat].max()
    norm_df[cat] = (norm_df[cat] - col_min) / (col_max - col_min) * 100

# ——— 4. LOWESS Smoothing —————————————————————————————————————————————————
smoothed = {
    cat: lowess(norm_df[cat], norm_df['decade'], frac=LOWESS_FRAC, return_sorted=False)
    for cat in CATEGORIES
}

# ——— 5. Plot Trends with Genre Annotations —————————————————————————————————
plt.figure(figsize=(11, 6))

# Plot each category’s smoothed trend and raw points
for cat in CATEGORIES:
    x = norm_df['decade']
    y = norm_df[cat]
    plt.plot(x, smoothed[cat],        color=COLORS[cat], lw=2, label=cat)
    plt.scatter(x, y, color=COLORS[cat], s=18, alpha=0.7)

# Add genre annotation boxes
for x, y, label in zip(GENRE_YEARS, GENRE_Y_POS, GENRE_LABELS):
    plt.text(
        x, y, label,
        ha='center', va='bottom',
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
    )

# Configure axes and legend
plt.title(
    "Psychological Lexicon Trends in English-Language Fiction (1800–2010)\n"
    "0–100 Normalised Scores",
    pad=15
)
plt.xlabel("Year")
plt.ylabel("Normalised Score (0–100)")
plt.xlim(1800, 2030)
plt.ylim(0, 100)
plt.yticks(np.arange(0, 101, 20))
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.legend(loc='center right', frameon=True)
plt.tight_layout()

# ——— 6. Save & Show —————————————————————————————————————————————————————
plt.savefig(FIGURE_PATH, dpi=150, bbox_inches='tight')
plt.show()