# ────────────────────────────────────────────────────────────────────────────────
# 1. Load required libraries
# ────────────────────────────────────────────────────────────────────────────────
library(dplyr)        # data manipulation
library(tidyverse)    # includes ggplot2, purrr, readr, tibble, etc.
library(hathiTools)   # HathiTrust-specific utilities
library(arrow)        # for efficient columnar data formats (if needed)

# ────────────────────────────────────────────────────────────────────────────────
# 2. Read HTIDs and define cache directory
# ────────────────────────────────────────────────────────────────────────────────
# Read the file of HathiTrust IDs (one per line)
hathi_ids <- readLines("hathiids.txt") %>%
  trimws() %>%                   # strip whitespace
  discard(~ .x == "")            # remove any empty lines

# Where hathiTools will cache/extract page‐counts data
cache_dir <- "~/data/EF"
options(hathiTools.ef.dir = cache_dir)


# ────────────────────────────────────────────────────────────────────────────────
# 3. Initialize logging of processed and failed IDs
# ────────────────────────────────────────────────────────────────────────────────
log_file <- "processed_ids.log"

# Load already‐processed IDs, if any
processed_ids <- if (file.exists(log_file)) {
  unique(readLines(log_file, warn = FALSE))
} else {
  character()
}
processed_ids_set <- as.character(processed_ids)

# Open the log connection for appending new IDs
log_con <- file(log_file, if (file.exists(log_file)) "a" else "w")

# Track IDs for which processing fails
failed_ids <- character()


# ────────────────────────────────────────────────────────────────────────────────
# 4. Split IDs into batches
# ────────────────────────────────────────────────────────────────────────────────
batch_size <- 100  # tune this based on memory/throughput

# Create a list of ID‐batches, each of length ≤ batch_size
batches <- split(
  hathi_ids,
  ceiling(seq_along(hathi_ids) / batch_size)
)


# ────────────────────────────────────────────────────────────────────────────────
# 5. Main processing loop: fetch, filter, write tokens
# ────────────────────────────────────────────────────────────────────────────────
for (batch_idx in seq_along(batches)) {
  cat("Processing batch", batch_idx, "of", length(batches), "\n")
  batch_ids <- batches[[batch_idx]]
  
  for (htid in batch_ids) {
    # Skip already‐processed IDs
    if (htid %in% processed_ids_set) {
      message("Skipping ID ", htid, ": previously processed")
      next
    }
    
    # Prepare a safe output filename
    safe_htid <- gsub("[^A-Za-z0-9.=+-]", "_", htid)
    out_file  <- paste0(safe_htid, ".txt")
    
    # If file already exists, log and skip
    if (file.exists(out_file)) {
      message("Skipping ID ", htid, ": file already exists")
      write(htid, file = log_con)
      processed_ids_set <- c(processed_ids_set, htid)
      next
    }
    
    # ────────────
    # 5A. Fetch and filter counts
    # ────────────
    data <- tryCatch({
      get_hathi_counts(
        htid,
        dir           = cache_dir,
        cache_format  = getOption("hathiTools.cacheformat")
      ) %>%
        filter(section == "body") %>%
        select(token, count, page)
    }, error = function(e) {
      message("Error fetching counts for ", htid, ": ", e$message)
      failed_ids <<- c(failed_ids, htid)
      NULL
    })
    
    # Skip if fetch failed or no body‐section data
    if (is.null(data) || nrow(data) == 0) {
      if (!is.null(data)) {
        message("No 'body' data for ID ", htid)
        failed_ids <<- c(failed_ids, htid)
      }
      next
    }
    
    # ─────────────────────────────────────────────────────────────────────────────
    # 5B. Expand tokens by count and group by page into lines of text
    # ─────────────────────────────────────────────────────────────────────────────
    token_data <- data %>%
      group_by(page) %>%
      summarise(
        tokens = list(rep(token, count)),
        .groups = "drop"
      ) %>%
      arrange(page)
    
    # ────────────
    # 5C. Write out one line per page
    # ────────────
    tryCatch({
      lines <- lapply(token_data$tokens, paste, collapse = " ")
      writeLines(unlist(lines), out_file)
      cat("Written to", out_file, "\n")
      
      # Log success
      write(htid, file = log_con)
      processed_ids_set <- c(processed_ids_set, htid)
    }, error = function(e) {
      message("Error writing file for ", htid, ": ", e$message)
      failed_ids <<- c(failed_ids, htid)
    }, finally = {
      # Clean up memory between IDs
      rm(data, token_data)
      gc(full = FALSE)
    })
  }
  
  # ensure all logs are flushed to disk after each batch
  flush(log_con)
  cat("Completed batch", batch_idx, "\n")
}


# ────────────────────────────────────────────────────────────────────────────────
# 6. Finalize: close logs and report failures
# ────────────────────────────────────────────────────────────────────────────────
close(log_con)

if (length(failed_ids) > 0) {
  writeLines(failed_ids, "failed_ids.txt")
  cat("Failed IDs written to failed_ids.txt\n")
} else {
  cat("All IDs processed successfully; no failures\n")
}