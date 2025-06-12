# HathiTrust-Psychological-Lexicon-Analysis
This repository can be used to replicate the analysis descirbed in the paper titled 'Lexical Contours of the Mind and Experience: A Computational History of Psychological Categories in Fiction' presented at KTUDELL conference.

This repository contains scripts for downloading, processing, and analyzing text data from the HathiTrust Digital Library, focusing on psychological lexicon trends and linguistic comparisons between fiction and non-fiction texts. The scripts include tools for downloading extracted features (EFs), performing statistical analyses, and visualizing trends over time.

## Repository Contents

This project includes the following files:

1. 1. download_EFs_and_write_to_txts.R  
   - Purpose: Downloads extracted feature (EF) counts from HathiTrust for a list of HathiTrust IDs (HTIDs), filters for body text, and writes tokens to individual text files (one file per HTID, one line per page).
   - Dependencies: R packages `dplyr`, `tidyverse`, `hathiTools`, `arrow`.
   - Input: A text file `hathiids.txt` containing one HTID per line.
   - Output: 
     - Text files named `<HTID>.txt` containing page-level token data.
     - `processed_ids.log`: Log of successfully processed HTIDs.
     - `failed_ids.txt`: Log of HTIDs that failed processing (if any).
   - Usage:
     ```bash
     Rscript 1_download_EFs_and_write_to_txts.R
     ```
     Ensure the `hathiids.txt` file is in the working directory and the cache directory (`~/data/EF`) exists with write permissions. Adjust `batch_size` in the script for memory optimization.

2. 2. rsync_booknlp_supersense_files.txt  
   - Purpose: Contains an `rsync` command to download BookNLP supersense data from HathiTrust's analytics server.
   - Dependencies: `rsync` installed on your system and access to HathiTrust's data analytics server.
   - Output: Downloads `booknlp_supersense.txt` to `/Desktop/booknlp-data`.
   - Usage:
     ```bash
     rsync data.analytics.hathitrust.org::booknlp/booknlp_supersense.txt /Desktop/booknlp-data
     ```
     Ensure the `/Desktop/booknlp-data` directory exists before running the command.

     2.1. Filter affect, cognition and perception categories from the all supersense files.

     2.2. Combine the wordlist with LIWC dictionary to get the final combined *.dicx file to be used with LIWC software.

     2.3. Run LIWC with CAP_final_combined.dicx dictionary on the corpus and save the output.

3. 3. MannWhitney U test.py  
   - Purpose: Performs Mann-Whitney U tests to compare LIWC (Linguistic Inquiry and Word Count) category scores (`Affect`, `Cognition`, `Perception`) between fiction and non-fiction datasets, with Bonferroni correction.
   - Dependencies: Python packages `pandas`, `numpy`, `scipy`.
   - Input:
     - `/data/FIC_LIWC_filtered_date_10190.xlsx`: Fiction LIWC data.
     - `/data/NONFIC_LIWC_filtered_10169.xlsx`: Non-fiction LIWC data.
   - Output: A DataFrame printed to the console with test results (U statistic, z-score, p-value, effect size, etc.).
   - Usage:
     ```bash
     python3 3_MannWhitney_U_test.py
     ```
     Update file paths in the script to match your local data locations.

4. 4. Linear regression.py  
   - Purpose: Fits OLS linear regression models to analyze trends in LIWC scores (`Affect`, `Cognition`, `Perception`) across decades, producing an APA-style results table and plots with 95% confidence intervals.
   - Dependencies: Python packages `pandas`, `numpy`, `statsmodels`, `matplotlib`.
   - Input: `/data/FIC_LIWC_filtered_date_10190.csv`
   - Output:
     - Console output: APA-style table of regression results.
     - Plots: Scatter plots with OLS fit and 95% CI for each LIWC category.
   - Usage:
     ```bash
     python3 4_Linear_regression.py
     ```
     Update `DATA_PATH` in the script to match your local file location.

5. 5. Trends visual.py  
   - Purpose: Visualizes normalized LIWC scores (`Affect`, `Cognition`, `Perception`) over decades using LOWESS smoothing, with genre annotations for English-language fiction (1800–2010).
   - Dependencies: Python packages `pandas`, `numpy`, `matplotlib`, `statsmodels`.
   - Input: `data/FIC_LIWC_filtered_date_10190.csv`
   - Output: A figure saved as `/data/Figure_4_trends.png` and displayed on-screen.
   - Usage:
     ```bash
     python3 5_Trends_visual.py
     ```
     Update `DATA_PATH` and `FIGURE_PATH` in the script to match your local file locations. Install `statsmodels` if not already installed (`pip install statsmodels`).

## Setup Instructions

### Prerequisites
- R: Install R and required packages:
  ```bash
  install.packages(c("dplyr", "tidyverse", "hathiTools", "arrow"))
  ```
- Python: Install Python 3 and required packages:
  ```bash
  pip install pandas numpy scipy statsmodels matplotlib
  ```
- rsync: Ensure `rsync` is installed for downloading BookNLP data (e.g., `sudo apt install rsync` on Linux).
- HathiTrust Access: Ensure you have access to HathiTrust's data analytics server for `rsync` and `hathiTools`.

### Directory Setup
1. Create a project directory (e.g., `HathiTrust_Text_Analysis`).
2. Place all scripts (`1_download_EFs_and_write_to_txts.R`, `2_rsync_booknlp_supersense_files.txt`, etc.) in the project directory.
3. Create a cache directory for `hathiTools` (e.g., `~/data/EF`) and ensure write permissions.
4. Ensure input files (`hathiids.txt`, LIWC `.csv` and `.xlsx` files) are accessible at the paths specified in the scripts, or update the paths accordingly.
5. Create the `/data/booknlp-data` directory for BookNLP supersense data, or modify the destination in `2_rsync_booknlp_supersense_files.txt`.

## Usage Workflow
1. Download BookNLP Data: Run the `rsync` command from `2_rsync_booknlp_supersense_files.txt` to download supersense data.
2. Download and Process EFs: Run `1_download_EFs_and_write_to_txts.R` to fetch and process HathiTrust extracted features into text files.
3. Statistical Analysis:
   - Run `3_MannWhitney_U_test.py` to compare LIWC scores between fiction and non-fiction.
   - Run `4_Linear_regression.py` to analyze LIWC score trends over time with OLS regression.
4. Visualize Trends: Run `5_Trends_visual.py` to generate a plot of normalized LIWC scores with genre annotations.

## Notes
- Ensure sufficient disk space for downloaded data, especially for `hathiTools` cache and output text files.
- Adjust `batch_size` in `1_download_EFs_and_write_to_txts.R` based on your system's memory capacity.
- Update file paths in Python scripts to match your local environment.
- The LIWC data files (`FIC_LIWC_filtered_date_10190.csv`, `.xlsx`, etc.) must be obtained separately and placed in the appropriate directories.
- For HathiTrust access issues, refer to [HathiTrust Data Analytics](https://www.hathitrust.org/data).

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or issues, please open an issue on this GitHub repository.
