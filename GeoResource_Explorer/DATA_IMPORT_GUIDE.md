# How to Import Trusted Mineral Deposits Data

## Overview

The GeoResource_Explorer application now includes a framework to import mineral deposits data from **trusted sources**. This guide explains how to obtain real data and import it into the database.

## Where to Get Trusted Data

### 1. **U.S. Geological Survey (USGS)**
   - **Website**: https://www.usgs.gov/faqs/what-are-major-mineral-deposits-world
   - **Mineral Commodity Summaries**: Published annually
   - **South Sudan Coverage**: Limited but available
   - **Cost**: Free
   - **Data Format**: Reports (PDF), need manual compilation

   **To Get Data**:
   ```
   Visit: https://pubs.usgs.gov/periodicals/mcs/
   Look for: Africa minerals, South Sudan references
   Download: Annual mineral commodity summaries
   ```

### 2. **World Bank - Extractive Industries Transparency Initiative (EITI)**
   - **Website**: https://eiti.org/
   - **Coverage**: Mining company production data
   - **Quality**: Government-reported, transparent
   - **Cost**: Free
   - **Format**: Reports, limited South Sudan data

   **To Get Data**:
   ```
   Check if South Sudan is EITI compliant
   Contact: eiti@eiti.org
   ```

### 3. **British Geological Survey (BGS)**
   - **Website**: https://www.bgs.ac.uk/
   - **Africa Program**: Regional assessments
   - **Cost**: Free datasets available
   - **Data Format**: Shapefiles, reports

   **To Get Data**:
   ```
   Visit: https://www.bgs.ac.uk/datasets/
   Search for Africa, mineral resources
   Download Africa Groundwater Atlas (related)
   ```

### 4. **Mining Companies (Public Reports)**
   - **ICMM Members**: International Council on Mining & Metals
   - **Companies with South Sudan operations**:
     - Pan African Resources plc
     - AngloGold Ashanti
     - Caroil Gold Resources
   - **Cost**: Free (public reports)
   - **Data Format**: Spreadsheets, quarterly/annual reports

   **To Get Data**:
   ```
   Visit company investor relations pages
   Download: Annual reports, sustainability reports
   Search for: "South Sudan", "mineral resources", "reserves"
   ```

### 5. **African Union - Mineral Resources Database**
   - **Website**: https://au.int/
   - **Coverage**: Continental mineral data
   - **Cost**: Free
   - **Availability**: Contact necessary

   **To Get Data**:
   ```
   Contact: African Union Commission
   Addis Ababa, Ethiopia
   Topic: NEPAD mining initiatives
   ```

### 6. **Academic & Research Institutions**
   - **University of Khartoum** (Sudan regional studies)
   - **African Minerals Geoscience Center**
   - **Society of Economic Geologists**
   - **Cost**: Variable (often free academic access)

### 7. **South Sudan Government Ministry**
   - **Ministry of Petroleum and Mining**
   - **Location**: Juba, South Sudan
   - **Data**: Official licensing records, geological surveys
   - **Cost**: May require formal request
   - **Challenges**: Limited online availability

   **To Contact**:
   ```
   Email: mining@mpm.gov.ss (if available)
   Address: Ministries Complex, CPA Road, Juba
   Method: Official government information request
   ```

## Data Import Process

### Step 1: Prepare Your CSV File

Create a CSV file with mineral deposits data. Use the sample template:

```bash
cd /workspaces/MY-PROJECTS/GeoResource_Explorer/app
python import_trusted_data.py create-sample
```

This creates `sample_deposits_import.csv` with the following structure:

```csv
name,mineral_type,ore_type,region,location_name,latitude,longitude,estimated_reserves_tonnes,average_grade,confidence_level,status,discovery_year,notes
Juba North Gold,Gold,Vein deposits,Central Equatoria,North of Juba city,5.00,31.65,350000,2.8,indicated,exploration,2018,USGS Report 2018
```

**Field Definitions**:

| Field | Required | Type | Example | Notes |
|-------|----------|------|---------|-------|
| name | Yes | Text | "Juba Gold Field" | Unique deposit name |
| mineral_type | Yes | Text | "Gold" | Must match database mineral_types |
| ore_type | Yes | Text | "Vein deposits" | Must match database ore_types |
| region | Yes | Text | "Central Equatoria" | South Sudan state name |
| location_name | No | Text | "25km NE of Juba" | Detailed location description |
| latitude | No | Float | 5.15 | WGS84 coordinate |
| longitude | No | Float | 31.30 | WGS84 coordinate |
| estimated_reserves_tonnes | No | Number | 500000 | Total tonnes of ore |
| average_grade | No | Float | 2.5 | g/tonne for gold, % for others |
| confidence_level | No | Text | "indicated" | confirmed, probable, possible |
| status | No | Text | "exploration" | active, inactive, exploration, under_development |
| discovery_year | No | Integer | 2018 | Year of discovery |
| notes | No | Text | "USGS Report" | Data source citation |

**Valid Mineral Types**:
- Gold
- Diamond
- Copper
- Oil & Gas
- Rare Earth Elements

**Valid Ore Types**:
- Vein deposits
- Placer deposits
- Porphyry ore
- Oxidized ore
- Primary ore

**Valid States**:
- Central Equatoria
- Eastern Equatoria
- Jonglei
- Lakes
- Northern Bahr el Ghazal
- Upper Nile
- Warrap
- West Equatoria
- Unity

### Step 2: Fill in Your Real Data

Edit `sample_deposits_import.csv` with actual data from your trusted sources:

```bash
nano app/sample_deposits_import.csv
# or use your text editor
```

### Step 3: Import the Data

```bash
cd /workspaces/MY-PROJECTS/GeoResource_Explorer/app

# Basic import
python import_trusted_data.py import sample_deposits_import.csv "USGS 2020 Reports"

# Specify confidence level
python import_trusted_data.py import sample_deposits_import.csv "USGS 2020 Reports" verified

# Or from Python
python -c "
from import_trusted_data import import_deposits_from_csv
import_deposits_from_csv('sample_deposits_import.csv', 'USGS 2020', 'verified')
"
```

### Step 4: Verify the Import

```bash
python import_trusted_data.py list-sources
```

This displays all registered data sources and their credibility levels.

## Data Source Tracking

The system automatically tracks:

- **Data Source Name** (e.g., "USGS 2020 Reports")
- **Credibility Level** (verified, unverified, pending)
- **Import Date** (timestamp)
- **Citation** (for each deposit)
- **Verification Status** (pending, verified, disputed)

This allows you to:
1. Know the origin of each piece of data
2. Track data quality and reliability
3. Update data when new sources become available
4. Generate reports with proper citations

## Python API Usage

### Import Deposits Programmatically

```python
from import_trusted_data import import_deposits_from_csv

# Import from CSV
success = import_deposits_from_csv(
    csv_file_path='my_data.csv',
    data_source='USGS 2020 Mineral Commodity Summaries',
    confidence_level='verified'  # or 'unverified', 'pending'
)

if success:
    print("Data imported successfully")
```

### List All Data Sources

```python
from import_trusted_data import list_data_sources

list_data_sources()
```

### Query Data by Source

```python
import sqlite3

conn = sqlite3.connect('minerals.db')
cur = conn.cursor()

# Get all deposits from a specific source
cur.execute("""
    SELECT d.name, d.region, m.name as mineral, ds.name as source
    FROM deposits d
    JOIN mineral_types m ON d.mineral_type_id = m.id
    JOIN deposit_sources dsrc ON d.id = dsrc.deposit_id
    JOIN data_sources ds ON dsrc.source_id = ds.id
    WHERE ds.name LIKE '%USGS%'
    ORDER BY d.region
""")

for deposit_name, region, mineral, source in cur.fetchall():
    print(f"• {deposit_name} ({mineral}) - {region} - {source}")

conn.close()
```

## Data Quality Standards

When importing data, ensure it meets these standards:

### Minimum Requirements
- [ ] Clear deposit name
- [ ] Mineral type (correctly spelled)
- [ ] Geographic location (region and coordinates if possible)
- [ ] Ore type classification

### Recommended Fields
- [ ] Reserve estimates (with units)
- [ ] Grade estimates (with units)
- [ ] Confidence level (measured/indicated/inferred)
- [ ] Discovery year
- [ ] Current status
- [ ] Data source citation

### Quality Indicators
- **Verified**: Data from official government or peer-reviewed sources
- **Indicated**: Data from reputable mining companies or surveys
- **Possible**: Data from preliminary studies or indirect sources

## Example Data Import Workflow

```bash
# Step 1: Create template
python import_trusted_data.py create-sample

# Step 2: Download real data (example)
# Visit: https://www.usgs.gov/centers/south-africa/south-sudan-mineral-resources
# Save as: usgs_south_sudan_2024.csv

# Step 3: Prepare CSV (open in Excel/LibreOffice)
# Map columns to match template:
# - USGS "Deposit Name" → our "name"
# - USGS "Commodity" → our "mineral_type"
# - etc.

# Step 4: Import
python import_trusted_data.py import usgs_south_sudan_2024.csv "USGS 2024 South Sudan Survey" verified

# Step 5: Verify
python import_trusted_data.py list-sources
```

## Troubleshooting

### "Mineral type 'X' not found"
**Solution**: Check available mineral types in the database
```python
import sqlite3
conn = sqlite3.connect('minerals.db')
cur = conn.cursor()
cur.execute("SELECT name FROM mineral_types")
print([row[0] for row in cur.fetchall()])
conn.close()
```

### "Region 'X' not found"
**Solution**: Check available South Sudan states
```python
import sqlite3
conn = sqlite3.connect('minerals.db')
cur = conn.cursor()
cur.execute("SELECT name FROM ss_states")
print([row[0] for row in cur.fetchall()])
conn.close()
```

### CSV Import Errors
- Ensure UTF-8 encoding
- Check for comma placement in text fields (use quotes)
- Verify all required columns are present
- Check for duplicate deposit names

## Next Steps

1. **Obtain Data**: Contact one of the trusted sources above
2. **Prepare CSV**: Use the sample template to format your data
3. **Import**: Run the import script with your data
4. **Verify**: Check that data imported correctly
5. **Cite**: Ensure proper citation of all data sources

## Support

For issues with the import framework:
```bash
cd /workspaces/MY-PROJECTS/GeoResource_Explorer/app
python import_trusted_data.py  # Shows usage
```

For data source recommendations or specific regions, consult:
- USGS Mineral Commodity Summaries
- World Bank's Extractive Industries Transparency Initiative
- Your country's official mineral surveys
