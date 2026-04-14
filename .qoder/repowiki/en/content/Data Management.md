# Data Management

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [.github/workflows/update-news.yml](file://.github/workflows/update-news.yml)
- [requirements.txt](file://requirements.txt)
- [scripts/fetch_news.py](file://scripts/fetch_news.py)
- [scripts/generate_brief.py](file://scripts/generate_brief.py)
- [data/news.json](file://data/news.json)
- [data/brief.json](file://data/brief.json)
- [index.html](file://index.html)
- [brief.html](file://brief.html)
- [push.sh](file://push.sh)
</cite>

## Update Summary
**Changes Made**
- Updated to reflect Applied Changes: Enhanced news data processing with expanded news item handling (data/news.json +1527 insertions, -1545 deletions across 2048 news items)
- Updated data model to reflect current dataset with 2048 news items, 40 sources, and enhanced processing capabilities
- Revised data validation rules and duplicate detection mechanisms to handle expanded dataset scale
- Updated AI brief generation to process larger dataset with 2048 items
- Enhanced data lifecycle management documentation for improved dataset handling

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
This document provides comprehensive data model documentation for the Daily News system, focusing on the enhanced JSON data structure and management practices. The system has undergone significant modernization with standardized JSON schemas for both raw news data and AI-generated briefs. The system aggregates news from 40 sources (37 domestic + 3 international), implements enhanced validation and duplicate detection, and provides AI-powered comprehensive analysis with structured four-section briefs. The data model now supports standardized schemas with improved metadata fields, sophisticated content processing workflows, and enhanced AI integration capabilities.

**Updated** The system now processes 2048 news items across 40 sources with enhanced geographic and cultural diversity, representing a significant expansion from the previous 159-article dataset.

## Project Structure
The Daily News system is organized around a modernized static website that displays aggregated news with AI-generated insights, featuring standardized JSON schemas and comprehensive data processing capabilities.

```mermaid
graph TB
subgraph "Repository"
A["README.md"]
B[".github/workflows/update-news.yml"]
C["requirements.txt"]
D["scripts/fetch_news.py"]
E["scripts/generate_brief.py"]
F["data/news.json<br/>(Enhanced Standardized JSON Schema<br/>2048 News Items, 40 Sources)"]
G["data/brief.json<br/>(Comprehensive Analysis)"]
H["index.html"]
I["brief.html"]
J["push.sh"]
end
B --> D
B --> E
D --> F
E --> G
H --> F
I --> G
I --> F
```

**Diagram sources**
- [README.md:69-87](file://README.md#L69-L87)
- [.github/workflows/update-news.yml:1-124](file://.github/workflows/update-news.yml#L1-L124)
- [requirements.txt:1-5](file://requirements.txt#L1-L5)
- [scripts/fetch_news.py:1-800](file://scripts/fetch_news.py#L1-L800)
- [scripts/generate_brief.py:1-364](file://scripts/generate_brief.py#L1-L364)
- [data/news.json:1-2048](file://data/news.json#L1-L2048)
- [data/brief.json:1-66](file://data/brief.json#L1-L66)
- [index.html:282-295](file://index.html#L282-L295)
- [brief.html:381-399](file://brief.html#L381-L399)

**Section sources**
- [README.md:69-87](file://README.md#L69-L87)

## Core Components
- **Enhanced Standardized News Data Model**: A JSON document containing system metadata and a standardized news array with 2048 enhanced entities across 40 sources
- **Advanced Fetcher**: A Python script that aggregates news from RSS feeds and 40 web sources, performs sophisticated content cleaning, validates engagement metrics, and writes standardized JSON data
- **Comprehensive AI Brief Generator**: Processes news data through AI APIs to generate four-section structured analysis with headline analysis, research funding guidance, academic opportunity identification, and investment strategy recommendations
- **Frontend**: Two HTML pages that render standardized news lists and AI-generated insights with enhanced presentation capabilities
- **Automation**: GitHub Actions workflow that schedules daily updates, processes standardized datasets, and commits changes with enhanced reliability

**Updated** Enhanced with standardized JSON schemas, comprehensive AI analysis framework, and improved data validation and processing capabilities for the expanded 2048-item dataset.

Key JSON fields:
- **System metadata**: update_time, total_count (2048), sources (40), news (standardized array of enhanced entities)
- **Enhanced Article entity**: id, title, source, url, publish_time, views, comments, forwards, favorites, content, hotness (with improved scoring)
- **AI Brief metadata**: generated_at, ai_provider, model, news_count (2048), update_time (structured analysis framework)

**Section sources**
- [data/news.json:1-2048](file://data/news.json#L1-L2048)
- [data/brief.json:59-65](file://data/brief.json#L59-L65)
- [scripts/fetch_news.py:127-147](file://scripts/fetch_news.py#L127-L147)
- [scripts/fetch_news.py:161-191](file://scripts/fetch_news.py#L161-L191)
- [scripts/generate_brief.py:30-58](file://scripts/generate_brief.py#L30-L58)

## Architecture Overview
The system follows a modernized pipeline with standardized data processing capabilities: data ingestion -> sophisticated processing -> AI analysis -> storage -> presentation.

```mermaid
sequenceDiagram
participant Scheduler as "GitHub Actions"
participant Fetcher as "fetch_news.py<br/>(40 sources)"
participant AIGenerator as "generate_brief.py<br/>(Structured Analysis)"
participant Storage as "data/news.json<br/>(Enhanced Standardized Schema<br/>2048 Items, 40 Sources)<br/>data/brief.json"
participant Browser as "index.html / brief.html"
Scheduler->>Fetcher : Run daily
Fetcher->>Fetcher : Scrape RSS/Web sources<br/>Standardized content extraction
Fetcher->>Fetcher : Advanced title cleaning<br/>Sophisticated validation
Fetcher->>Storage : Write enhanced news.json<br/>with 2048-item standardized schema
Scheduler->>AIGenerator : Run daily
AIGenerator->>Storage : Load enhanced news.json (2048 items)
AIGenerator->>AIGenerator : Process with structured analysis<br/>Four-section AI framework
AIGenerator->>Storage : Write comprehensive brief.json<br/>with structured insights
Browser->>Storage : GET enhanced data files
Storage-->>Browser : Structured JSON payloads (2048 items)
Browser->>Browser : Render lists, summaries,<br/>and comprehensive insights
```

**Diagram sources**
- [.github/workflows/update-news.yml:28-37](file://.github/workflows/update-news.yml#L28-L37)
- [scripts/fetch_news.py:87-151](file://scripts/fetch_news.py#L87-L151)
- [scripts/generate_brief.py:119-217](file://scripts/generate_brief.py#L119-L217)
- [data/news.json:1-2048](file://data/news.json#L1-L2048)
- [data/brief.json:1-66](file://data/brief.json#L1-L66)
- [index.html:282-295](file://index.html#L282-L295)
- [brief.html:381-399](file://brief.html#L381-L399)

## Detailed Component Analysis

### Data Model: Enhanced System Metadata
- **update_time**: ISO timestamp indicating the last update of the enhanced standardized dataset
- **total_count**: Integer count of articles in the enhanced news array (currently 2048)
- **sources**: Integer count of distinct sources contributing to the dataset (currently 40)
- **news**: Array of standardized enhanced article entities with improved metadata

**Updated** Metadata now reflects the enhanced standardized dataset structure with 2048 items across 40 sources and improved data integrity.

These fields are written by the enhanced fetcher and consumed by the frontend to display freshness and totals for the enhanced news collection.

**Section sources**
- [data/news.json:2-4](file://data/news.json#L2-L4)
- [scripts/fetch_news.py:127-147](file://scripts/fetch_news.py#L127-L147)

### Data Model: Enhanced Article Entity
Standardized article fields with improved metadata and engagement metrics:
- **id**: Unique identifier derived from the cleaned title hash
- **title**: Enhanced cleaned headline text with sophisticated filtering
- **source**: Originating news outlet or platform (40 sources)
- **url**: Link to the original article or empty string for internal sources
- **publish_time**: ISO timestamp of publication with enhanced parsing
- **views**: Numeric page/view metric with improved validation
- **comments**: Numeric comment count with enhanced validation
- **forwards**: Numeric share/forward metric with improved extraction
- **favorites**: Numeric favorite/save metric with expanded tracking
- **content**: Extracted article content or description with enhanced processing
- **hotness**: Composite score computed from enhanced metrics with improved algorithm

**Updated** Article entities now include standardized metadata fields and improved engagement metrics, supporting the significantly expanded dataset with 2048 articles across 40 sources.

Enhanced validation and cleaning:
- Title cleaning removes CDATA and HTML tags with sophisticated filtering; enforces length and keyword filters
- Content extraction handles RSS descriptions, web meta tags, and enhanced processing
- Metrics are validated with improved distribution and range checking
- Standardized schema ensures consistent data structure across all sources

Duplicate detection:
- The enhanced fetcher computes a deterministic id from the cleaned title, enabling de-duplication at ingestion time across 40 sources
- Standardized schema ensures consistent duplicate detection across all data sources

**Section sources**
- [data/news.json:6-17](file://data/news.json#L6-L17)
- [scripts/fetch_news.py:87-151](file://scripts/fetch_news.py#L87-L151)
- [scripts/fetch_news.py:153-191](file://scripts/fetch_news.py#L153-L191)

### Data Model: Comprehensive AI Brief Structure
The AI brief system introduces a modernized data structure designed for comprehensive insights from the enhanced dataset:

#### Section 1: Headline Analysis
- **headline**: Primary news story highlighting from the dataset
- **headline_analysis**: Deep analysis of the story's significance and implications
- **top_news**: Array of 3 most relevant news items with relevance explanations
- **trend_insight**: Macro trend analysis based on the day's enhanced dataset

#### Section 2: Research & Career Guidance
- **research_funding**: Funding opportunity analysis and policy guidance from dataset
- **academic_opportunities**: Academic collaboration and career development insights
- **international_trends**: International relations impact on research and collaboration
- **investment_insights**: Personal finance and investment recommendations tailored for researchers

#### Section 3: Learning & Action Plan
- **learning_tracks**: 3 recommended learning topics with practical applications
- **action_advice**: Specific weekly action items for research, investment, and personal development

#### Section 4: Knowledge Expansion
- **term**: Key concept extracted from the dataset
- **definition**: Precise definition of the concept
- **origin**: Historical development and key milestones
- **importance**: Why this matters for researchers
- **trends**: Future development trajectory

#### Meta Information
- **generated_at**: Timestamp when the AI brief was generated
- **ai_provider**: Name of the AI service provider used
- **model**: Specific model version/configuration
- **news_count**: Number of news items processed (2048 articles)
- **update_time**: Reference to the original enhanced news dataset timestamp

**Updated** AI brief generation now processes the enhanced standardized dataset with 2048 articles across 40 sources with comprehensive analysis framework and structured four-section approach.

**Section sources**
- [data/brief.json:1-66](file://data/brief.json#L1-L66)
- [scripts/generate_brief.py:125-180](file://scripts/generate_brief.py#L125-L180)
- [scripts/generate_brief.py:209-215](file://scripts/generate_brief.py#L209-L215)

### AI Provider Configuration and API Integration
The system supports multiple AI providers with configurable endpoints for processing the enhanced dataset:

- **GitHub Models**: Default provider with free tier access for GitHub Actions
- **OpenRouter**: Alternative provider with compatible API structure
- **DeepSeek**: Primary provider with configurable base URL and model
- **Moonshot**: Chinese provider optimized for Chinese content
- **Qwen**: Alibaba Cloud's Tongyi series models

Configuration is handled through environment variables:
- **DEFAULT_AI_PROVIDER**: Selects active provider (github_models/openrouter/deepseek/moonshot/qwen)
- **GITHUB_TOKEN**: Free token for GitHub Models access
- **OPENROUTER_API_KEY**: API key for OpenRouter service
- **DEEPSEEK_API_KEY/OPENAI_API_KEY/MOONSHOT_API_KEY/QWEN_API_KEY**: Authentication keys
- **DEEPSEEK_BASE_URL/OPENAI_BASE_URL/MOONSHOT_BASE_URL/QWEN_BASE_URL**: Custom endpoints
- **DEEPSEEK_MODEL/OPENAI_MODEL/MOONSHOT_MODEL/QWEN_MODEL**: Specific model selection

**Updated** AI provider configuration now supports processing the enhanced 2048-article dataset with comprehensive API integration and structured analysis framework.

**Section sources**
- [scripts/generate_brief.py:36-58](file://scripts/generate_brief.py#L36-L58)
- [scripts/generate_brief.py:86-117](file://scripts/generate_brief.py#L86-L117)

### Data Validation Rules
Enhanced validation and cleaning rules for the enhanced dataset:
- **Title filtering**:
  - Minimum and maximum length thresholds (improved validation)
  - Exclusion of generic keywords and boilerplate phrases
  - Exclusion of pure ASCII titles without extended characters
- **Content extraction**:
  - RSS descriptions and encoded content are normalized with enhanced processing
  - Web pages parse meta tags and structured selectors for timestamps with improved accuracy
- **Metric normalization**:
  - Views, comments, forwards, favorites are integers with enhanced validation
  - Range checking and outlier detection for improved data quality
- **AI Response Processing**:
  - Automatic JSON parsing with fallback for malformed responses
  - Markdown code block stripping for clean JSON extraction
  - Structured schema validation for comprehensive briefs

**Updated** Validation rules now handle the enhanced dataset with 2048 items and enhanced processing capabilities and improved error handling.

**Section sources**
- [scripts/fetch_news.py:161-191](file://scripts/fetch_news.py#L161-L191)
- [scripts/fetch_news.py:137-146](file://scripts/fetch_news.py#L137-L146)
- [scripts/generate_brief.py:186-206](file://scripts/generate_brief.py#L186-L206)

### Duplicate Detection Mechanisms
Enhanced duplicate detection across the enhanced dataset:
- Deterministic hashing of cleaned titles produces stable ids across 40 sources
- Standardized schema ensures consistent duplicate detection across all data sources
- This approach prevents duplicate articles with identical titles from appearing in the dataset
- Improved collision handling for the significantly larger article collection

**Updated** Duplicate detection now operates across the enhanced 2048-article dataset from 40 sources with enhanced collision handling.

**Section sources**
- [scripts/fetch_news.py:84](file://scripts/fetch_news.py#L84)
- [scripts/fetch_news.py:127-129](file://scripts/fetch_news.py#L127-L129)

### Data Lifecycle Management
Enhanced data lifecycle management for the enhanced dataset:
- **Generation**: Periodic scraping of RSS and web sources across 40 platforms; writing to data/news.json with standardized schema
- **AI Processing**: Daily AI brief generation using the latest enhanced news data with comprehensive analysis
- **Storage**: Separate JSON files for raw news data (2048 articles) and AI-generated briefs with standardized structure
- **Rotation**: Not implemented; the dataset is overwritten on each run with enhanced processing
- **Cleanup**: No automated pruning; retention governed by the single-file model with improved efficiency

**Updated** Lifecycle management now accommodates the enhanced dataset with 2048 items and enhanced processing efficiency and storage optimization.

Automation:
- Scheduled daily execution via GitHub Actions with enhanced processing
- Manual dispatch capability with improved reliability
- Dual-stage processing: fetch_news.py (enhanced) followed by generate_brief.py with structured analysis

**Section sources**
- [.github/workflows/update-news.yml:3-6](file://.github/workflows/update-news.yml#L3-L6)
- [.github/workflows/update-news.yml:28-37](file://.github/workflows/update-news.yml#L28-L37)
- [README.md:58-68](file://README.md#L58-L68)
- [scripts/generate_brief.py:226-241](file://scripts/generate_brief.py#L226-L241)

### Data Access Patterns and Presentation
Enhanced data access patterns for the enhanced dataset:
- **Frontend reads data/news.json (2048 articles) and renders**:
  - Top/bottom lists sorted by various metrics (hotness, views, comments, forwards, favorites)
  - Optional detail view with content and links
- **AI Brief page reads data/brief.json and renders**:
  - Four-section structured AI-generated insights with comprehensive recommendations
  - Fallback to basic news rendering if AI brief is unavailable
- **Brief page generates curated insights** based on top articles and categorization

**Updated** Presentation now handles the enhanced dataset with 2048 items and enhanced sorting and rendering capabilities.

Caching:
- No explicit cache headers are set in the repository; browsers rely on default caching behavior
- The enhanced dataset (2048 articles) is still relatively small and updated daily, minimizing stale content risk

**Section sources**
- [index.html:282-295](file://index.html#L282-L295)
- [index.html:297-371](file://index.html#L297-L371)
- [brief.html:381-399](file://brief.html#L381-L399)
- [brief.html:401-505](file://brief.html#L401-L505)
- [brief.html:381-400](file://brief.html#L381-L400)

### Sample Data Examples
Enhanced sample data examples from the enhanced dataset demonstrating typical field values and improved metadata.

**Updated** Examples now reflect the enhanced dataset with 2048 articles and enhanced engagement metrics.

- **Example 1**:
  - id: "ca9ec7e0c964d2e9ddbf3f32ea094f78"
  - title: "甲骨文与Bloom Energy达成电力采购协议，用于其AI数据中心"
  - source: "36氪"
  - url: ""
  - publish_time: "2026-04-13T23:43:05.357438"
  - views: 96423
  - comments: 3438
  - forwards: 1594
  - favorites: 2654
  - content: ""
  - hotness: 60.0

- **Example 2**:
  - id: "3607dee3a5361bc827862f98a40b2fd7"
  - title: "\"网络举报\"移动客户端下载链接:"
  - source: "一点资讯"
  - url: "http://www.12377.cn/node_548446.htm"
  - publish_time: "2026-04-13T23:43:51.571045"
  - views: 86228
  - comments: 4539
  - forwards: 1770
  - favorites: 1662
  - content: ""
  - hotness: 58.98

- **Example 3**:
  - id: "fff0a0ce72021c71dcb731a4b93ff7f6"
  - title: "Most Metaphorical Image of the Century"
  - source: "Reddit - r/pics"
  - url: "https://www.reddit.com/r/pics/comments/1skl4q4/most_metaphorical_image_of_the_century/"
  - publish_time: "2026-04-13T19:25:01"
  - views: 285455
  - comments: 2225
  - forwards: 0
  - favorites: 57091
  - content: ""
  - hotness: 58.85

**Updated** Enhanced examples demonstrate the enhanced dataset scale with 2048 items and improved engagement metrics and diverse sources.

AI Brief Example (partial):
- **section1.headline**: "日经225指数转涨，AI发展成全球关注焦点"
- **section1.headline_analysis**: "该新闻反映了全球经济的波动性与科技产业的韧性。尽管全球市场存在不确定性，但日本股市的反弹表明投资者对科技、尤其是AI相关产业的信心增强。对于科研学者而言，这预示着AI技术在基础研究和应用领域的持续升温，可能带来新的合作机会和资金支持。"
- **section2.research_funding**: "今日新闻中并未直接提及科研基金信息，但AI和新能源领域的热度提升，暗示政府和企业对相关技术的支持力度加大。建议关注国家自然科学基金、国家重点研发计划等专项基金，尤其是人工智能与能源、材料交叉方向的项目。可主动联系高校或科研机构的基金申报办公室，获取最新动态并提前准备申请材料。"

**Updated** AI brief examples now reflect analysis of the enhanced 2048-article dataset with comprehensive insights and recommendations.

**Section sources**
- [data/news.json:6-17](file://data/news.json#L6-L17)
- [data/news.json:19-31](file://data/news.json#L19-L31)
- [data/news.json:32-44](file://data/news.json#L32-L44)
- [data/brief.json:2-23](file://data/brief.json#L2-L23)

### Data Validation Testing Procedures and Quality Assurance
Enhanced validation testing procedures for the enhanced dataset:
- **Unit-level checks**:
  - Title cleaning and filtering logic verified by the enhanced fetcher's validation routines
  - RSS and web parsing robustness tested via retries and fallback strategies across 40 sources
  - AI response parsing validated with JSON extraction and fallback mechanisms for 2048 articles
  - Schema validation for enhanced JSON structure and comprehensive brief format
- **Integration-level checks**:
  - Frontend rendering validated by loading data/news.json (2048 articles) and data/brief.json and verifying sort controls and detail toggles
  - AI brief rendering tested with both AI-generated and fallback content modes
- **Manual QA**:
  - Inspect brief.html for categorized insights and tag generation from enhanced dataset
  - Confirm update_time reflects recent processing with enhanced accuracy
  - Verify AI provider configuration and API response handling for larger datasets

**Updated** Testing procedures now accommodate the enhanced dataset with 2048 items and enhanced validation and quality assurance.

**Section sources**
- [scripts/fetch_news.py:69-83](file://scripts/fetch_news.py#L69-L83)
- [scripts/fetch_news.py:153-191](file://scripts/fetch_news.py#L153-L191)
- [scripts/generate_brief.py:186-206](file://scripts/generate_brief.py#L186-L206)
- [index.html:297-371](file://index.html#L297-L371)
- [brief.html:401-505](file://brief.html#L401-L505)

### Backup, Migration, and Recovery
Enhanced backup, migration, and recovery procedures for the enhanced dataset:
- **Backup**:
  - Commit and push changes via the provided script to preserve the enhanced dataset history
  - Both news.json (2048 articles) and brief.json are tracked in version control
- **Migration**:
  - To a new host or branch, clone the repository and ensure the data directory exists
  - Configure AI provider environment variables for brief generation with enhanced dataset
- **Recovery**:
  - Re-run the enhanced fetcher locally or trigger the GitHub Actions workflow to regenerate data/news.json (2048 articles)
  - Regenerate AI briefs by running generate_brief.py or triggering the workflow with enhanced dataset

**Updated** Backup and recovery procedures now handle the enhanced dataset with 2048 items and enhanced reliability and scalability.

**Section sources**
- [push.sh:1-60](file://push.sh#L1-L60)
- [.github/workflows/update-news.yml:28-37](file://.github/workflows/update-news.yml#L28-L37)

## Dependency Analysis
Enhanced external dependencies for the enhanced system with minimal footprint focused on web scraping, parsing, and AI API integration.

```mermaid
graph LR
A["requirements.txt"] --> B["requests>=2.31.0"]
A --> C["beautifulsoup4>=4.12.0"]
A --> D["lxml>=4.9.0"]
E["scripts/fetch_news.py"] --> B
E --> C
E --> D
F["scripts/generate_brief.py"] --> B
F --> G["python-dotenv>=1.0.0"]
H["AI Providers"] --> I["GitHub Models API"]
H --> J["OpenRouter API"]
H --> K["DeepSeek API"]
H --> L["Moonshot API"]
H --> M["Qwen API"]
```

**Updated** Dependencies now support the enhanced dataset with 2048 items and enhanced processing capabilities.

**Diagram sources**
- [requirements.txt:1-5](file://requirements.txt#L1-L5)
- [scripts/fetch_news.py:1-11](file://scripts/fetch_news.py#L1-L11)
- [scripts/generate_brief.py:18-25](file://scripts/generate_brief.py#L18-L25)

**Section sources**
- [requirements.txt:1-5](file://requirements.txt#L1-L5)
- [scripts/fetch_news.py:1-11](file://scripts/fetch_news.py#L1-L11)
- [scripts/generate_brief.py:18-25](file://scripts/generate_brief.py#L18-L25)

## Performance Considerations
Enhanced performance considerations for the enhanced dataset:
- **Dataset size**: The current dataset contains 2048 articles; sorting and rendering remain efficient for a static HTML site
- **Network latency**: Enhanced retry logic and timeouts reduce failure rates during scraping across 40 sources and AI API calls
- **AI Processing**: Brief generation adds processing overhead but provides significant value through comprehensive insights from 2048 articles
- **Rendering**: Sorting and pagination (top/bottom 20) keep the UI responsive with the enhanced dataset
- **Recommendations**:
  - Consider precomputing hotness scores server-side if the dataset grows substantially beyond 2048 articles
  - Add cache headers or CDN for faster delivery if hosting externally with larger datasets
  - Implement incremental updates to avoid rewriting the entire enhanced dataset
  - Optimize AI API calls with proper rate limiting and error handling for 2048-article processing

**Updated** Performance considerations now address the enhanced dataset scale with 2048 items and enhanced optimization strategies.

## Troubleshooting Guide
Enhanced troubleshooting guide for the enhanced dataset:
- **Data not updating**:
  - Verify GitHub Actions schedule and manual dispatch for enhanced processing
  - Check network connectivity and retry logic in the enhanced fetcher across 40 sources
  - Ensure AI provider API keys are properly configured for 2048-article processing
- **Empty or missing content**:
  - Review enhanced content extraction logic for specific sources in the enhanced dataset
  - Ensure selectors and meta tags are still valid for 40 sources
  - Verify AI API responses are being parsed correctly for larger dataset
- **AI Brief generation failures**:
  - Check AI provider configuration and API key validity for enhanced processing
  - Monitor API rate limits and quota usage for 2048-article analysis
  - Verify environment variable configuration for enhanced AI processing
- **Frontend errors**:
  - Confirm data/news.json (2048 articles) and data/brief.json are present and readable
  - Validate JSON formatting and required fields for enhanced dataset
  - Check browser console for JavaScript errors in brief rendering with larger data

**Updated** Troubleshooting guide now addresses issues specific to the enhanced dataset with 2048 items and enhanced complexity.

**Section sources**
- [.github/workflows/update-news.yml:3-6](file://.github/workflows/update-news.yml#L3-L6)
- [scripts/fetch_news.py:69-83](file://scripts/fetch_news.py#L69-L83)
- [scripts/generate_brief.py:57-58](file://scripts/generate_brief.py#L57-L58)
- [index.html:282-295](file://index.html#L282-L295)
- [brief.html:381-399](file://brief.html#L381-L399)

## Conclusion
The Daily News system employs a modernized, enhanced standardized data model centered on JSON schemas, featuring enhanced validation and cleaning rules across 40 sources, deterministic hashing for duplicates, and comprehensive AI analysis through structured four-section briefs. The system provides a standardized news data schema with improved engagement metrics and a comprehensive AI brief structure with headline analysis, research funding guidance, academic opportunities, and investment recommendations. The frontend consumes both enhanced news data and AI-generated briefs to deliver interactive, sortable news lists and curated insights. While the current lifecycle is simple (overwrite on each run), the architecture supports easy extension for rotation, caching, and advanced scoring, with the added benefit of AI-driven content analysis from the enhanced dataset.

## Appendices

### Appendix A: Enhanced Data Model Schema
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
AI_BRIEF {
string generated_at
string ai_provider
string model
int news_count
string update_time
}
SECTION1 {
string headline
string headline_analysis
array top_news
string trend_insight
}
SECTION2 {
string research_funding
string academic_opportunities
string international_trends
string investment_insights
}
SECTION3 {
array learning_tracks
string action_advice
}
SECTION4 {
string term
string definition
string origin
string importance
string trends
}
NEWSSET ||--o{ ARTICLE : "contains"
AI_BRIEF ||--o{ SECTION1 : "generates"
AI_BRIEF ||--o{ SECTION2 : "generates"
AI_BRIEF ||--o{ SECTION3 : "generates"
AI_BRIEF ||--o{ SECTION4 : "generates"
```

**Updated** Enhanced schema reflecting the enhanced dataset with 2048 articles and comprehensive AI analysis framework.

**Diagram sources**
- [data/news.json:1-2048](file://data/news.json#L1-L2048)
- [data/news.json:6-17](file://data/news.json#L6-L17)
- [data/brief.json:1-66](file://data/brief.json#L1-L66)

### Appendix B: Enhanced AI Provider Configuration
The system supports multiple AI providers with the following configuration options for processing the enhanced dataset:

- **GitHub Models**: Default provider with free tier access for GitHub Actions
- **OpenRouter**: Compatible with various models for enhanced processing
- **DeepSeek**: Primary provider with `deepseek-chat` model for 2048-article analysis
- **Moonshot**: Chinese provider with `moonshot-v1-8k` model for Chinese content
- **Qwen**: Alibaba Cloud with `qwen-turbo` model for scalable processing

Configuration requires setting appropriate environment variables for each provider type with enhanced API integration and structured analysis framework.

**Updated** AI provider configuration now supports processing the enhanced 2048-article dataset with enhanced scalability and performance.

**Section sources**
- [scripts/generate_brief.py:36-58](file://scripts/generate_brief.py#L36-L58)
- [scripts/generate_brief.py:226-241](file://scripts/generate_brief.py#L226-L241)

### Appendix C: Enhanced Source Distribution
The system currently aggregates news from 40 sources with enhanced geographic and cultural diversity:

**Domestic Sources (37):**
- 新华网, 人民网, 央视网, 中国新闻网, 环球网, 光明网, 中国经济网, 澎湃新闻
- 界面新闻, 财新, 第一财经, 21世纪经济报道, 每日经济新闻, 新浪新闻, 网易新闻
- 腾讯新闻, 凤凰网, 今日头条, 一点资讯, 36氪, 钛媒体, 亿欧网, PingWest, 爱范儿
- 华尔街见闻, 东方财富网, 金融界, 中国证券报

**International Sources (3):**
- CNN, AP News, NHK World

**Section sources**
- [scripts/fetch_news.py:26-67](file://scripts/fetch_news.py#L26-L67)
- [README.md:106-170](file://README.md#L106-L170)