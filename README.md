# Prime Time Medical Research Opportunities Identifier

## Alpha Version Proof of Concept

This application helps identify subfields of medicine that are "prime" for new research by analyzing publication and citation data from PubMed and CrossRef.

## Features

- Search PubMed for medical research articles
- Store articles in a PostgreSQL database
- Analyze research opportunities by subfield
- Calculate metrics including publication count, citation counts, and opportunity score
- View detailed article information

## Prerequisites

- PostgreSQL database server (locally installed or remote)
- Internet connection for PubMed and CrossRef API access

## Installation

### Option 1: Run from executable

1. Download the latest release executable
2. Run the executable file

### Option 2: Run from source

1. Clone this repository
2. Install Python 3.x if not already installed
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python main.py
   ```

## Building the Executable

To build the executable yourself:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Make the build script executable:
   ```
   chmod +x build_exe.sh
   ```

3. Run the build script:
   ```
   ./build_exe.sh
   ```

4. The executable will be created in the `dist` folder

## Database Setup

1. Install and start PostgreSQL
2. Create a database named "prime_time" (or choose your own name)
3. In the application, enter your database credentials and click "Connect"
4. Click "Initialize DB" to create the necessary tables

## Usage

1. Connect to your PostgreSQL database using the form at the top
2. Search for medical articles using the Search bar or explore specific subfields using the dropdown
3. View the articles in the database and double-click an article to see full details
4. Check the Opportunity Analysis section to see metrics for the selected subfield

## Architecture

This application follows the architecture outlined in the Prime Time Medical Research Opportunities Identifier planning document:

- **Data Sources**: PubMed API (via Biopython) and CrossRef API for citation data
- **Database**: PostgreSQL for storing article metadata, authors, and citation information
- **Backend**: Python with psycopg2 for database access
- **Frontend**: Tkinter GUI

## Limitations of Alpha Version

This is a proof-of-concept with the following limitations:

- Basic UI with limited visualization capabilities
- Simple opportunity scoring algorithm
- Limited error handling and validation
- No user authentication or multi-user support

## Future Enhancements

Future versions will include:

- Machine learning model for better opportunity scoring
- Trend analysis and predictions
- Advanced data visualization
- Web-based interface
- User accounts and saved searches
- Integration with more data sources

## Credits

Created as an alpha version of the Prime Time Medical Research Opportunities Identifier project.