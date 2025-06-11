import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu

# Load the LIWC data
fic = pd.read_excel('/mnt/data/FIC_LIWC_filtered_date_10190.xlsx')
nonfic = pd.read_excel('/mnt/data/NONFIC_LIWC_filtered_10169.xlsx')

# Define the LIWC categories of interest
categories = ['Affect', 'Cognition', 'Perception']

# Prepare to collect results
results = []
n1, n2 = len(fic), len(nonfic)

for cat in categories:
    data1 = fic[cat].dropna()
    data2 = nonfic[cat].dropna()
    
    # Compute median and IQR
    med1 = data1.median()
    q1_1 = data1.quantile(0.25)
    q3_1 = data1.quantile(0.75)
    iqr1 = q3_1 - q1_1
    
    med2 = data2.median()
    q1_2 = data2.quantile(0.25)
    q3_2 = data2.quantile(0.75)
    iqr2 = q3_2 - q1_2
    
    # Mann–Whitney U test
    U, p_val = mannwhitneyu(data1, data2, alternative='two-sided')
    
    # Approximate z-value for the U statistic
    mean_U = n1 * n2 / 2
    std_U = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (U - mean_U) / std_U
    
    # Effect size r
    r = z / np.sqrt(n1 + n2)
    
    # Bonferroni correction (3 tests)
    p_bonf = min(p_val * len(categories), 1.0)
    
    # Store results
    results.append({
        'Category': cat,
        'Fiction Median (IQR)': f"{med1:.2f} ({iqr1:.2f})",
        'Non-fiction Median (IQR)': f"{med2:.2f} ({iqr2:.2f})",
        'U': int(U),
        'z': round(z, 2),
        'p': p_val,
        'r': round(r, 2),
        'p (Bonf.)': p_bonf
    })

# Create DataFrame of results
results_df = pd.DataFrame(results)

