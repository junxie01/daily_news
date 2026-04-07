# Data Management

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [.github/workflows/update-news.yml](file://.github/workflows/update-news.yml)
- [requirements.txt](file://requirements.txt)
- [scripts/fetch_news.py](file://scripts/fetch_news.py)
- [data/news.json](file://data/news.json)
- [index.html](file://index.html)
- [brief.html](file://brief.html)
- [push.sh](file://push.sh)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document provides comprehensive data model documentation for the Daily News system, focusing on the JSON data structure and management practices. It covers the news article entity schema, system metadata, validation and cleaning rules, duplicate detection mechanisms, lifecycle management, access patterns, caching strategies, performance considerations, testing procedures, and backup/recovery guidelines. The goal is to enable both technical and non-technical stakeholders to understand how news data is generated, stored, rotated, and consumed.

## Project Structure
The Daily News system is organized around a static website that displays aggregated news from multiple sources. Data is fetched periodically via a Python script, processed into a single JSON file, and rendered by HTML pages.

```mermaid
graph TB
subgraph "Repository"
A["README.md"]
B[".github/workflows/update-news.yml"]
C["requirements.txt"]
D["scripts/fetch_news.py"]
E["data/news.json"]
F["index.html"]
G["brief.html"]
H["push.sh"]
end
B --> D
D --> E
F --> E
G --> E
```

**Diagram sources**
- [README.md:48-62](file://README.md#L48-L62)
- [.github/workflows/update-news.yml:1-38](file://.github/workflows/update-news.yml#L1-L38)
- [requirements.txt:1-4](file://requirements.txt#L1-L4)
- [scripts/fetch_news.py:1-25](file://scripts/fetch_news.py#L1-L25)
- [data/news.json:1-10](file://data/news.json#L1-L10)
- [index.html:282-295](file://index.html#L282-L295)
- [brief.html:381-399](file://brief.html#L381-L399)

**Section sources**
- [README.md:48-62](file://README.md#L48-L62)

## Core Components
- Data model: A JSON document containing system metadata and a news array of article entities.
- Fetcher: A Python script that aggregates news from RSS feeds and selected web sources, cleans titles, validates content, and writes the JSON file.
- Frontend: Two HTML pages that read the JSON file and render news lists and summaries.
- Automation: A GitHub Actions workflow that schedules daily updates and commits changes.

Key JSON fields:
- System metadata: update_time, total_count, sources, news (array).
- Article entity: id, title, source, url, publish_time, views, comments, forwards, favorites, content, hotness.

Validation and cleaning rules are implemented in the fetcher to ensure consistent, usable data.

**Section sources**
- [data/news.json:1-10](file://data/news.json#L1-L10)
- [scripts/fetch_news.py:127-147](file://scripts/fetch_news.py#L127-L147)
- [scripts/fetch_news.py:161-191](file://scripts/fetch_news.py#L161-L191)

## Architecture Overview
The system follows a pipeline: data ingestion -> processing -> storage -> presentation.

```mermaid
sequenceDiagram
participant Scheduler as "GitHub Actions"
participant Fetcher as "fetch_news.py"
participant Storage as "data/news.json"
participant Browser as "index.html / brief.html"
Scheduler->>Fetcher : Run daily
Fetcher->>Fetcher : Scrape RSS/Web sources
Fetcher->>Fetcher : Clean titles, validate content
Fetcher->>Storage : Write JSON with metadata + news[]
Browser->>Storage : GET data/news.json
Storage-->>Browser : JSON payload
Browser->>Browser : Render lists and summaries
```

**Diagram sources**
- [.github/workflows/update-news.yml:28-37](file://.github/workflows/update-news.yml#L28-L37)
- [scripts/fetch_news.py:87-151](file://scripts/fetch_news.py#L87-L151)
- [data/news.json:1-10](file://data/news.json#L1-L10)
- [index.html:282-295](file://index.html#L282-L295)
- [brief.html:381-399](file://brief.html#L381-L399)

## Detailed Component Analysis

### Data Model: System Metadata
- update_time: ISO timestamp indicating the last update of the dataset.
- total_count: Integer count of articles in the news array.
- sources: Integer count of distinct sources contributing to the dataset.
- news: Array of article entities.

These fields are written by the fetcher and consumed by the frontend to display freshness and totals.

**Section sources**
- [data/news.json:2-4](file://data/news.json#L2-L4)
- [scripts/fetch_news.py:127-147](file://scripts/fetch_news.py#L127-L147)

### Data Model: Article Entity
Article fields:
- id: Unique identifier derived from the title hash.
- title: Cleaned headline text.
- source: Originating news outlet or platform.
- url: Link to the original article.
- publish_time: ISO timestamp of publication.
- views: Numeric page/view metric.
- comments: Numeric comment count.
- forwards: Numeric share/forward metric.
- favorites: Numeric favorite/save metric.
- content: Extracted article content or description.
- hotness: Composite score computed from metrics.

Validation and cleaning:
- Title cleaning removes CDATA and HTML tags; enforces length and keyword filters.
- Content extraction handles RSS descriptions and web meta tags.
- Metrics are randomized placeholders in the current implementation.

Duplicate detection:
- The fetcher computes a deterministic id from the cleaned title, enabling de-duplication at ingestion time.

Hotness scoring:
- The README describes a multi-factor scoring mechanism combining views, comments, forwards, favorites, and recency. The current dataset includes a hotness field; the exact formula is not embedded in the repository files.

**Section sources**
- [data/news.json:6-17](file://data/news.json#L6-L17)
- [scripts/fetch_news.py:87-151](file://scripts/fetch_news.py#L87-L151)
- [scripts/fetch_news.py:153-191](file://scripts/fetch_news.py#L153-L191)
- [README.md:9](file://README.md#L9)

### Data Validation Rules
- Title filtering:
  - Minimum and maximum length thresholds.
  - Exclusion of generic keywords and boilerplate phrases.
  - Exclusion of pure ASCII titles without extended characters.
- Content extraction:
  - RSS descriptions and encoded content are normalized.
  - Web pages parse meta tags and structured selectors for timestamps.
- Metric normalization:
  - Views, comments, forwards, favorites are integers; randomized in current implementation.

**Section sources**
- [scripts/fetch_news.py:161-191](file://scripts/fetch_news.py#L161-L191)
- [scripts/fetch_news.py:137-146](file://scripts/fetch_news.py#L137-L146)

### Duplicate Detection Mechanisms
- Deterministic hashing of cleaned titles produces stable ids.
- This approach prevents duplicate articles with identical titles from appearing in the dataset.

**Section sources**
- [scripts/fetch_news.py:84](file://scripts/fetch_news.py#L84)
- [scripts/fetch_news.py:127-129](file://scripts/fetch_news.py#L127-L129)

### Data Lifecycle Management
- Generation: Periodic scraping of RSS and web sources; writing to data/news.json.
- Storage: Single JSON file with metadata and news array.
- Rotation: Not implemented; the dataset is overwritten on each run.
- Cleanup: No automated pruning; retention governed by the single-file model.

Automation:
- Scheduled daily execution via GitHub Actions.
- Manual dispatch capability.

**Section sources**
- [.github/workflows/update-news.yml:3-6](file://.github/workflows/update-news.yml#L3-L6)
- [.github/workflows/update-news.yml:28-37](file://.github/workflows/update-news.yml#L28-L37)
- [README.md:37-46](file://README.md#L37-L46)

### Data Access Patterns and Presentation
- Frontend reads data/news.json and renders:
  - Top/bottom lists sorted by various metrics (hotness, views, comments, forwards, favorites).
  - Optional detail view with content and links.
- Brief page generates curated insights based on top articles and categorization.

Caching:
- No explicit cache headers are set in the repository; browsers rely on default caching behavior. The dataset is small and updated daily, minimizing stale content risk.

**Section sources**
- [index.html:282-295](file://index.html#L282-L295)
- [index.html:297-371](file://index.html#L297-L371)
- [brief.html:381-399](file://brief.html#L381-L399)
- [brief.html:401-505](file://brief.html#L401-L505)

### Sample Data Examples
Below are representative entries from the dataset demonstrating typical field values. These examples reflect the current structure and placeholder metrics.

- Example 1:
  - id: "8df233bb73e6ebac76238e535c71c578"
  - title: "Employee lends account to trade stocks Bohai Securities receives regulatory warning"
  - source: "China Securities Journal"
  - url: "https://www.cs.com.cn/qs/2026/04/05/detail_2026040510001836.html"
  - publish_time: "2026-04-07T16:22:00"
  - views: 63060
  - comments: 3812
  - forwards: 1922
  - favorites: 2872
  - content: ""
  - hotness: 70.99

- Example 2:
  - id: "b7c8f18cd990afab4c308aeee2baaa96"
  - title: "European indices open higher | FTSE 100 up 0.17%, CAC 40 up 0.47%, DAX 30 up 0.10%, Milan MIB up 0.40%."
  - source: "First Financial"
  - url: "https://www.yicai.com/brief/103121099.html"
  - publish_time: "2026-04-07T15:27:04.644170"
  - views: 91683
  - comments: 2590
  - forwards: 1750
  - favorites: 2751
  - content: ""
  - hotness: 69.01

- Example 3:
  - id: "707b11723ada53f785a77b29de8d3e26"
  - title: "Dongying Huiyang green lithium battery new energy industry investment fund registered"
  - source: "36Kr"
  - url: ""
  - publish_time: "2026-04-07T15:26:50.523192"
  - views: 78235
  - comments: 3681
  - forwards: 1618
  - favorites: 2209
  - content: ""
  - hotness: 67.25

These examples illustrate the presence of empty content fields and placeholder metrics, consistent with the current dataset.

**Section sources**
- [data/news.json:6-17](file://data/news.json#L6-L17)
- [data/news.json:19-31](file://data/news.json#L19-L31)
- [data/news.json:32-44](file://data/news.json#L32-L44)

### Data Validation Testing Procedures and Quality Assurance
- Unit-level checks:
  - Title cleaning and filtering logic verified by the fetcher’s validation routines.
  - RSS and web parsing robustness tested via retries and fallback strategies.
- Integration-level checks:
  - Frontend rendering validated by loading data/news.json and verifying sort controls and detail toggles.
- Manual QA:
  - Inspect brief.html for categorized insights and tag generation.
  - Confirm update_time reflects recent processing.

**Section sources**
- [scripts/fetch_news.py:69-83](file://scripts/fetch_news.py#L69-L83)
- [scripts/fetch_news.py:153-191](file://scripts/fetch_news.py#L153-L191)
- [index.html:297-371](file://index.html#L297-L371)
- [brief.html:401-505](file://brief.html#L401-L505)

### Backup, Migration, and Recovery
- Backup:
  - Commit and push changes via the provided script to preserve dataset history.
- Migration:
  - To a new host or branch, clone the repository and ensure the data directory exists.
- Recovery:
  - Re-run the fetcher locally or trigger the GitHub Actions workflow to regenerate data/news.json.

**Section sources**
- [push.sh:1-60](file://push.sh#L1-L60)
- [.github/workflows/update-news.yml:28-37](file://.github/workflows/update-news.yml#L28-L37)

## Dependency Analysis
External dependencies are minimal and focused on web scraping and parsing.

```mermaid
graph LR
A["requirements.txt"] --> B["requests"]
A --> C["beautifulsoup4"]
A --> D["lxml"]
E["scripts/fetch_news.py"] --> B
E --> C
E --> D
```

**Diagram sources**
- [requirements.txt:1-4](file://requirements.txt#L1-L4)
- [scripts/fetch_news.py:1-11](file://scripts/fetch_news.py#L1-L11)

**Section sources**
- [requirements.txt:1-4](file://requirements.txt#L1-L4)
- [scripts/fetch_news.py:1-11](file://scripts/fetch_news.py#L1-L11)

## Performance Considerations
- Dataset size: The current dataset contains hundreds of articles; sorting and rendering remain efficient for a static HTML site.
- Network latency: Retry logic and timeouts reduce failure rates during scraping.
- Rendering: Sorting and pagination (top/bottom 20) keep the UI responsive.
- Recommendations:
  - Consider precomputing hotness scores server-side if the dataset grows substantially.
  - Add cache headers or CDN for faster delivery if hosting externally.
  - Implement incremental updates to avoid rewriting the entire dataset.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Data not updating:
  - Verify GitHub Actions schedule and manual dispatch.
  - Check network connectivity and retry logic in the fetcher.
- Empty or missing content:
  - Review content extraction logic for specific sources.
  - Ensure selectors and meta tags are still valid.
- Frontend errors:
  - Confirm data/news.json is present and readable.
  - Validate JSON formatting and required fields.

**Section sources**
- [.github/workflows/update-news.yml:3-6](file://.github/workflows/update-news.yml#L3-L6)
- [scripts/fetch_news.py:69-83](file://scripts/fetch_news.py#L69-L83)
- [index.html:282-295](file://index.html#L282-L295)
- [brief.html:381-399](file://brief.html#L381-L399)

## Conclusion
The Daily News system employs a straightforward, maintainable data model centered on a single JSON file. The fetcher enforces validation and cleaning rules, uses deterministic hashing for duplicates, and exposes a simple metadata schema. The frontend consumes this data to deliver interactive, sortable news lists and curated summaries. While the current lifecycle is simple (overwrite on each run), the architecture supports easy extension for rotation, caching, and advanced scoring.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Appendix A: Data Model Schema
```mermaid
erDiagram
NEWSSET {
string update_time
int total_count
int sources
}
ARTICLE {
string id PK
string title
string source
string url
string publish_time
int views
int comments
int forwards
int favorites
string content
float hotness
}
NEWSSET ||--o{ ARTICLE : "contains"
```

**Diagram sources**
- [data/news.json:1-10](file://data/news.json#L1-L10)
- [data/news.json:6-17](file://data/news.json#L6-L17)