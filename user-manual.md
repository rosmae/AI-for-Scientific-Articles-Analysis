# Prime Time Medical Research - User Manual

A comprehensive guide to using the AI-powered medical research opportunity analysis platform.

![Prime Time Medical Research](frontend/static/icon.ico)

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Research Search Workflow](#research-search-workflow)
4. [Articles Management](#articles-management)
5. [Analysis & Opportunity Scoring](#analysis--opportunity-scoring)
6. [Advanced Features](#advanced-features)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### First Time Setup

1. **Access the Application**
   - Open your web browser
   - Navigate to `http://localhost:5173`
   - You'll see the Prime Time Medical Research dashboard

2. **Check System Status**
   - Look for the green "✅ connected" status in the top-right corner
   - This indicates the backend API is running and connected

3. **Initial Exploration**
   - The application has three main sections: **Dashboard**, **Articles**, and **Analysis**
   - Use the navigation menu at the top to switch between sections

---

## 🏠 Dashboard Overview

The dashboard is your starting point for all research activities.

### Main Components

#### 🔍 Research Search Form
- **Research Idea Input**: Large text area for describing your research concept
- **AI Keyword Generation**: Automatically extract relevant keywords using PubMedBERT
- **Manual Keywords**: Edit or add keywords manually
- **Search Parameters**: Configure search settings and date ranges

#### 📅 Date Filter Options
- **Quick Presets**: One-click date ranges (1 year, 2 years, 5 years, 10 years, all time)
- **Custom Date Range**: Select specific start and end dates using calendar pickers
- **Date Range Display**: Visual confirmation of selected time period

#### 🔔 Notification System
- **Toast Messages**: Real-time feedback for all actions
- **Success Notifications**: Green messages with celebration emojis
- **Error Alerts**: Red messages with clear error descriptions
- **Auto-dismiss**: Notifications automatically fade after 5 seconds

---

## 🔬 Research Search Workflow

### Step 1: Enter Your Research Idea

1. **Click** in the "Research Idea" text area
2. **Type** your research concept in natural language
3. **Example**: *"machine learning applications in cancer diagnosis and treatment"*
4. **Minimum**: 10 characters required for processing

### Step 2: Generate AI-Powered Keywords

1. **Click** the "🧠 Generate Keywords" button
2. **Wait** for PubMedBERT processing (usually 5-10 seconds)
3. **Review** the generated keywords that appear below
4. **Keywords** are automatically populated in the search field with semicolon separators

#### Generated Keywords Panel
- **Primary Keywords**: Main terms extracted from your research idea
- **Relevance Scores**: Confidence scores (0.0 to 1.0) for each keyword
- **MeSH Expansion**: Medical vocabulary enhancements (when available)

### Step 3: Configure Search Parameters

#### Max Results Selection
- **5 articles**: Quick test searches
- **10 articles**: Standard searches
- **20 articles**: Comprehensive searches  
- **50 articles**: Extensive research
- **100 articles**: Maximum retrieval

#### Date Range Configuration
1. **Click** "📅 Show Date Filters" to expand date options
2. **Choose** a quick preset or set custom dates:
   - **Last Year**: Most recent publications
   - **Last 2 Years**: Recent developments
   - **Last 5 Years**: Current research trends (default)
   - **Last 10 Years**: Comprehensive historical view
   - **All Time**: Complete literature search

3. **Custom Dates**: Use calendar pickers for specific ranges
4. **Date Validation**: End date cannot be before start date or after today

### Step 4: Execute PubMed Search

1. **Click** "🔍 Search PubMed" button
2. **Watch** the loading indicator and progress messages
3. **Enjoy** the confetti celebration 🎉 when articles are successfully added!
4. **Review** the success notification with search statistics

#### Search Process Behind the Scenes
- **MeSH Expansion**: Keywords enhanced with medical vocabulary
- **PubMed Query**: Optimized search string constructed
- **Article Retrieval**: Full metadata and abstracts downloaded
- **Database Storage**: Articles saved with semantic vectors
- **Background Analysis**: Clustering and opportunity scoring initiated

---

## 📚 Articles Management

Navigate to the **Articles** page to browse and manage your research literature.

### Article Table Features

#### 📊 Pagination Controls
- **Items per Page**: Choose 5, 10, 20, or 50 articles per page
- **Page Navigation**: Previous/Next buttons and numbered pages
- **Jump to Page**: Type any page number and press Enter
- **Page Information**: "Showing X-Y of Z articles" status

#### 🔍 Search and Filter
1. **Search Box**: Type to filter articles by:
   - Article title
   - Abstract content
   - Journal name
   - Author names
   - PMID numbers

2. **Real-time Filtering**: Results update as you type
3. **Clear Search**: Button to reset filters
4. **Filter Counter**: Shows filtered vs. total articles

#### 📋 Sortable Columns
Click column headers to sort by:
- **Article Details**: Title and abstract preview
- **Journal & Authors**: Publication venue and author list
- **Date**: Publication date (newest first by default)
- **PMID**: PubMed identifier

#### 🔗 Article Actions
For each article, you can:
- **👁️ View Details**: Open individual article page with full information
- **🔗 DOI Link**: Open article on publisher website (if DOI available)
- **📖 PubMed**: View article on PubMed database

### Individual Article View

Click the "👁️" icon to view detailed article information:

#### Article Metadata
- **Full Title**: Complete article title
- **Complete Abstract**: Full abstract text
- **Publication Details**: Journal, date, volume, issue
- **Author Information**: Complete author list with affiliations
- **Citation Data**: Citation count and metrics
- **Identifiers**: PMID, DOI, and other identifiers

#### Navigation
- **Back to Articles**: Return to article table
- **Previous/Next**: Navigate between articles
- **External Links**: Quick access to PubMed and DOI

### Export Functionality

#### CSV Export
1. **Click** "📄 Export CSV" button
2. **File Download**: Automatic download starts
3. **Filename**: `articles_YYYY-MM-DD.csv` with current date
4. **Content**: All article metadata in spreadsheet format

#### Export Data Includes
- PMID, Title, Journal, Authors
- Publication Date, Abstract
- DOI, Citation Count
- Search Association Data

---

## 📊 Analysis & Opportunity Scoring

The **Analysis** page provides AI-powered insights into research opportunities.

### Search Selection

#### Enhanced Search Browser
- **Pagination**: View 6, 12, 24, or 48 searches per page
- **Search Filter**: Filter by research idea, keywords, or search ID
- **Search Cards**: Visual cards showing search metadata
- **Selection**: Click any search card to load its analysis

#### Search Card Information
- **Search ID**: Unique identifier
- **Research Idea**: Original research concept
- **Timestamp**: When the search was performed
- **Article Count**: Number of articles found
- **Status Indicator**: Analysis completion status

### Opportunity Scoring Dashboard

When you select a search, the analysis dashboard loads:

#### Overall Opportunity Score
- **Score Range**: 0.0 to 1.0 (higher is better)
- **Visual Indicator**: Color-coded score bar
- **Interpretation**: Detailed explanation of the score
- **Recommendation**: AI-generated research advice

#### Detailed Metrics

##### 🎯 Novelty Score (Semantic Uniqueness)
- **Purpose**: Measures how unique your research topic is
- **Calculation**: Semantic similarity vs. existing literature
- **Interpretation**:
  - **High (0.8+)**: Highly novel research area
  - **Medium (0.5-0.8)**: Moderately explored topic
  - **Low (0.0-0.5)**: Well-established research area

##### 📈 Citation Velocity Score (Impact Growth)
- **Purpose**: Measures the growth rate of citations in this area
- **Calculation**: Citation trajectory analysis over time
- **Interpretation**:
  - **High (0.8+)**: Rapidly growing field
  - **Medium (0.5-0.8)**: Steady citation growth
  - **Low (0.0-0.5)**: Declining or stable citations

##### ⏰ Recency Score (Timeliness)
- **Purpose**: Evaluates how recent the research activity is
- **Calculation**: Publication date distribution analysis
- **Interpretation**:
  - **High (0.8+)**: Very active, recent publications
  - **Medium (0.5-0.8)**: Moderate recent activity
  - **Low (0.0-0.5)**: Older, less active research area

### Background Analysis Status

#### Processing Indicators
- **Clustering**: Article grouping and similarity analysis
- **Forecasting**: Citation trend prediction using ARIMA
- **Scoring**: Opportunity metric calculation
- **Completion**: All analysis finished

#### Analysis Results
- **Article Clusters**: Groups of similar research papers
- **Research Trends**: Historical and predicted citation patterns
- **Opportunity Ranking**: Comparative scoring vs. other searches

---

## 🎨 Advanced Features

### Notification System

#### Success Notifications
- **🎉 Confetti Effects**: Celebration animations for successful actions
- **Green Toast Messages**: Positive feedback with emojis
- **Auto-celebration**: Confetti triggers automatically on article ingestion

#### Error Handling
- **Red Toast Messages**: Clear error descriptions
- **Retry Suggestions**: Helpful hints for resolving issues
- **Persistent Errors**: Stay visible until manually dismissed

### User Interface Enhancements

#### Responsive Design
- **Desktop Optimized**: Full feature access on large screens
- **Mobile Friendly**: Touch-optimized interface for phones and tablets
- **Adaptive Layout**: Automatically adjusts to screen size

#### Loading States
- **Progress Indicators**: Spinners and loading messages
- **Button States**: Disabled buttons during processing
- **Background Processing**: Non-blocking operations

#### Visual Feedback
- **Hover Effects**: Interactive elements respond to mouse
- **Active States**: Clear indication of current selections
- **Smooth Animations**: Transitions between states
- **Modern Icons**: Intuitive emoji and icon usage

### Keyboard Navigation

#### Shortcuts
- **Enter**: Submit forms and search fields
- **Escape**: Close modals and clear selections
- **Arrow Keys**: Navigate through pagination
- **Tab**: Move between form elements

---

## 💡 Tips & Best Practices

### Research Idea Formulation

#### Effective Research Ideas
✅ **Good**: "machine learning applications in cancer diagnosis"
✅ **Good**: "telemedicine impact on rural healthcare delivery"
✅ **Good**: "CRISPR gene editing for sickle cell disease treatment"

❌ **Avoid**: "cancer" (too broad)
❌ **Avoid**: "ML" (too abbreviated)
❌ **Avoid**: Single words or very short phrases

#### Optimization Tips
- **Be Specific**: Include specific methods, diseases, or applications
- **Use Medical Terms**: Include relevant medical vocabulary
- **Length**: 10-100 words work best
- **Context**: Provide enough context for accurate keyword generation

### Search Strategy

#### Keyword Refinement
1. **Review Generated Keywords**: Check AI suggestions for relevance
2. **Add Synonyms**: Include alternative terms manually
3. **Remove Irrelevant**: Delete keywords that don't match your focus
4. **Balance Breadth vs. Depth**: More keywords = broader search

#### Date Range Selection
- **Recent Work**: Last 1-2 years for cutting-edge research
- **Comprehensive**: Last 5-10 years for thorough review
- **Historical**: All time for complete literature coverage
- **Trending**: Last 2-3 years for emerging fields

### Result Optimization

#### Search Results Analysis
- **Quality Check**: Review article titles and abstracts
- **Relevance Assessment**: Ensure articles match your research focus
- **Diversity**: Look for different perspectives and approaches
- **Citation Impact**: Pay attention to highly cited works

#### Opportunity Score Interpretation
- **High Scores (0.8+)**: Excellent research opportunities
- **Medium Scores (0.5-0.8)**: Good potential with some competition
- **Low Scores (0.0-0.5)**: Saturated or declining areas

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Connection Problems
**Issue**: "Cannot connect to API server" message
**Solution**:
1. Verify the backend API is running on `localhost:8000`
2. Check that your firewall isn't blocking the connection
3. Try refreshing the page
4. Contact system administrator if problem persists

#### Search Not Working
**Issue**: No results or search fails
**Solution**:
1. Check your internet connection
2. Verify keywords are properly formatted (semicolon-separated)
3. Try broadening your search terms
4. Check if PubMed is accessible from your network

#### Slow Performance
**Issue**: Application responds slowly
**Solution**:
1. Close unnecessary browser tabs
2. Clear browser cache and cookies
3. Reduce the number of articles per page
4. Check your internet connection speed

#### Missing Articles
**Issue**: Expected articles don't appear
**Solution**:
1. Verify your date range includes the expected publication dates
2. Check if articles are in PubMed database
3. Try alternative keywords or broader search terms
4. Review MeSH term expansion results

### Error Messages

#### "Research idea too short"
- **Cause**: Less than 10 characters entered
- **Solution**: Provide a more detailed research description

#### "No keywords provided"
- **Cause**: Empty keyword field
- **Solution**: Generate keywords or enter them manually

#### "Database connection failed"
- **Cause**: Backend database issues
- **Solution**: Contact system administrator

#### "Rate limit exceeded"
- **Cause**: Too many requests to PubMed API
- **Solution**: Wait a few minutes before trying again

### Browser Compatibility

#### Supported Browsers
✅ **Chrome** 90+ (Recommended)
✅ **Firefox** 88+
✅ **Safari** 14+
✅ **Edge** 90+

#### Browser Requirements
- **JavaScript**: Must be enabled
- **Cookies**: Required for session management
- **Local Storage**: Used for temporary data
- **Modern ES2020**: Required for application features

### Performance Optimization

#### For Best Experience
- Use a modern browser with latest updates
- Ensure stable internet connection
- Close unnecessary applications
- Use recommended screen resolution (1920x1080 or higher)

---

## 📞 Support & Assistance

### Getting Help

#### Documentation
- **README.md**: Technical setup and configuration
- **API Documentation**: `http://localhost:8000/docs`
- **This Manual**: Comprehensive user guidance

#### Contact Information
- **Technical Issues**: Contact your system administrator
- **Feature Requests**: Submit through proper channels
- **Bug Reports**: Include browser, error message, and steps to reproduce

### Feedback and Improvement

Your feedback helps improve the Prime Time Medical Research platform:
- **User Experience**: Share your workflow suggestions
- **Feature Ideas**: Propose new functionality
- **Bug Reports**: Help us identify and fix issues
- **Success Stories**: Share how the platform helped your research

---

**Prime Time Medical Research** - Empowering medical research through AI-powered analysis! 🔬✨

*Last Updated: June 28, 2025*
