# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [scripts/fetch_news.py](file://scripts/fetch_news.py)
- [index.html](file://index.html)
- [data/news.json](file://data/news.json)
- [.github/workflows/update-news.yml](file://.github/workflows/update-news.yml)
- [push.sh](file://push.sh)
- [test_connections.py](file://test_connections.py)
- [brief.html](file://brief.html)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Quick Setup](#quick-setup)
4. [Local Development](#local-development)
5. [Basic Usage](#basic-usage)
6. [Command-Line Instructions](#command-line-instructions)
7. [GitHub Pages Deployment](#github-pages-deployment)
8. [Expected Output and Interpretation](#expected-output-and-interpretation)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Performance Considerations](#performance-considerations)
11. [Conclusion](#conclusion)

## Introduction
This guide helps you quickly set up and use the Daily News project locally and deploy it to GitHub Pages. The project automatically aggregates 24-hour trending news from multiple sources, computes a composite popularity score, and displays the results in an interactive web interface. You can run the news fetcher locally, preview the results in your browser, and optionally publish the site to GitHub Pages for public access.

## Prerequisites
Before starting, ensure you have:
- Python 3.x installed on your system
- Git installed and configured
- A modern web browser (Chrome, Firefox, Safari, Edge)
- Network connectivity to access external news websites during scraping

These requirements are essential for installing dependencies, running the Python script, and viewing the generated HTML pages.

**Section sources**
- [README.md:13-28](file://README.md#L13-L28)

## Quick Setup
Follow these steps to get the project running locally:

1. Clone the repository to your local machine using Git.
2. Navigate into the project directory.
3. Install Python dependencies using the provided requirements file.
4. Run the news fetcher script to generate the latest dataset.
5. Open the main HTML page in your browser to view the results.

These steps are described in the project’s quick start section and will be expanded below with precise commands and explanations.

**Section sources**
- [README.md:13-28](file://README.md#L13-L28)

## Local Development
This section walks you through setting up a local development environment and running the project end-to-end.

### Step 1: Clone the Repository
Clone the repository to your local machine using Git. This creates a local copy of the project files, including the Python script, HTML pages, and configuration files.

- Command: git clone <repository-url>
- Replace <repository-url> with your actual repository URL.

After cloning, navigate into the project directory.

### Step 2: Install Dependencies
Install the required Python packages using the provided requirements file. This ensures your environment has the libraries needed for web scraping and data processing.

- Command: pip install -r requirements.txt

The requirements file specifies the minimum versions for requests, beautifulsoup4, and lxml.

**Section sources**
- [requirements.txt:1-4](file://requirements.txt#L1-L4)

### Step 3: Run the News Fetcher Script
Execute the Python script that scrapes news sources, filters and deduplicates entries, computes scores, and writes the results to the data file.

- Command: python scripts/fetch_news.py

This script:
- Initializes a session with appropriate headers
- Scrapes RSS feeds and selected websites
- Filters titles based on length and content criteria
- Generates synthetic engagement metrics (views, comments, forwards, favorites)
- Writes a JSON file containing the latest news and metadata

Notes:
- Some sources may be temporarily unavailable; the script handles retries and continues processing other sources.
- The script logs progress and errors to the console.

**Section sources**
- [scripts/fetch_news.py:12-25](file://scripts/fetch_news.py#L12-L25)
- [scripts/fetch_news.py:69-83](file://scripts/fetch_news.py#L69-L83)
- [scripts/fetch_news.py:87-152](file://scripts/fetch_news.py#L87-L152)

### Step 4: Verify Data Generation
After running the script, confirm that the data file has been updated.

- Location: data/news.json
- The file contains:
  - An update timestamp
  - Total count and source counts
  - A list of news items with fields such as id, title, source, url, publish_time, views, comments, forwards, favorites, content, and hotness

If the file does not exist or appears empty, re-run the script and check the console output for errors.

**Section sources**
- [data/news.json:1-10](file://data/news.json#L1-L10)

## Basic Usage
Once the data file is generated, open the main HTML page in your browser to view the interactive news list.

- Open index.html in your browser
- The page loads data from data/news.json and renders:
  - Sortable columns (hotness, views, comments, forwards, favorites)
  - View modes (top 20 vs bottom 20)
  - Expandable news details with content and links
  - Update time indicator

You can switch sorting criteria and view modes using the buttons at the top of the page.

**Section sources**
- [index.html:282-295](file://index.html#L282-L295)
- [index.html:297-371](file://index.html#L297-L371)

## Command-Line Instructions
This section provides exact commands for both local execution and deployment scenarios.

### Local Execution Commands
- Install dependencies: pip install -r requirements.txt
- Run the fetcher: python scripts/fetch_news.py
- View results: open index.html in your browser

### GitHub Pages Deployment Commands
There are two primary approaches:

Option A: Manual Push Workflow
- Prepare changes locally
- Commit and push to your remote repository using SSH
- The push script automates adding, committing, rebasing, and pushing

Example commands:
- git add .
- git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
- git push origin main

Option B: Automated GitHub Actions
- The workflow runs daily at 23:00 UTC (corresponds to 07:00 Beijing time)
- It installs dependencies, runs the fetcher, and commits/pushes updates automatically
- You can also trigger the workflow manually from the Actions tab

**Section sources**
- [push.sh:1-60](file://push.sh#L1-L60)
- [.github/workflows/update-news.yml:1-38](file://.github/workflows/update-news.yml#L1-L38)

## GitHub Pages Deployment
You can deploy the project to GitHub Pages for public access.

### Steps to Deploy
1. Create a repository on GitHub and push your code to it.
2. Enable GitHub Pages in your repository settings:
   - Go to Settings → Pages
   - Choose the branch and folder (e.g., main branch with root directory)
3. Configure secrets if your workflow requires credentials (optional)
4. Optionally trigger the automated workflow manually from the Actions tab

The automated workflow:
- Runs daily at 23:00 UTC
- Installs Python 3.11
- Installs dependencies from requirements.txt
- Executes the fetcher script
- Commits and pushes the updated data file

**Section sources**
- [README.md:30-36](file://README.md#L30-L36)
- [.github/workflows/update-news.yml:18-37](file://.github/workflows/update-news.yml#L18-L37)

## Expected Output and Interpretation
After running the fetcher and opening index.html, you will see:
- A list of news items sorted by the selected metric (default: hotness)
- Each item shows:
  - Rank badge (1st, 2nd, 3rd highlighted)
  - Title and source
  - Publish time
  - Metrics: views, comments, forwards, favorites
  - Optional content preview and a link to the original article
- Update time reflects the last successful data generation

Interpretation tips:
- Hotness is a composite score derived from engagement metrics
- Views, comments, forwards, and favorites reflect community activity
- Click an item to expand and view content and the original link
- Use the “最热门20条” and “最冷门20条” buttons to toggle between top and bottom lists

Optional: Use brief.html for a curated research-oriented summary generated from the same dataset.

**Section sources**
- [index.html:297-371](file://index.html#L297-L371)
- [brief.html:381-399](file://brief.html#L381-L399)

## Troubleshooting Guide
Common setup and runtime issues, plus verification steps:

### Issue: Python dependencies missing or outdated
- Symptom: pip install fails or import errors occur
- Fix: Reinstall dependencies using the requirements file
- Verification: Confirm requests, beautifulsoup4, and lxml are present

**Section sources**
- [requirements.txt:1-4](file://requirements.txt#L1-L4)

### Issue: Network connectivity problems during scraping
- Symptom: Some sources fail to load or timeouts occur
- Fix: Retry the fetcher; it includes retry logic and continues on failures
- Verification: Check console output for attempt counts and error messages

**Section sources**
- [scripts/fetch_news.py:69-83](file://scripts/fetch_news.py#L69-L83)

### Issue: No data displayed in the browser
- Symptom: The page shows a message indicating no data
- Fix: Run the fetcher script to generate data/news.json
- Verification: Confirm data/news.json exists and contains recent update_time

**Section sources**
- [index.html:282-295](file://index.html#L282-L295)

### Issue: Automated workflow not updating data
- Symptom: GitHub Pages remains stale
- Fix: Manually trigger the workflow from the Actions tab or check workflow logs
- Verification: Review workflow logs for dependency installation and script execution

**Section sources**
- [.github/workflows/update-news.yml:1-38](file://.github/workflows/update-news.yml#L1-L38)

### Issue: Testing external site accessibility
- Use the connection tester script to verify access to major news sites
- Command: python test_connections.py

**Section sources**
- [test_connections.py:1-45](file://test_connections.py#L1-L45)

## Performance Considerations
- The fetcher script uses retries and randomized delays to reduce server pressure and improve reliability.
- The HTML page renders a fixed number of items (top 20) by default to keep the interface responsive.
- For large datasets, consider filtering or pagination strategies if extending the frontend.

[No sources needed since this section provides general guidance]

## Conclusion
You now have everything needed to run the Daily News project locally, view the generated news in your browser, and deploy it to GitHub Pages. Use the provided commands to install dependencies, run the fetcher, and open index.html. For automation, rely on the GitHub Actions workflow or the manual push script. If you encounter issues, consult the troubleshooting section and verify data generation and network access.

[No sources needed since this section summarizes without analyzing specific files]