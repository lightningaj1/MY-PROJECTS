# QGIS Data Import Guide

## Phase 8: Geospatial Data Management

This guide explains how to import mineral deposits and mining claims directly from QGIS (Quantum GIS) into GeoResource Explorer.

---

## Overview

The QGIS Data Import feature allows administrators to:
- **Import mineral deposits** from QGIS as GeoJSON or CSV
- **Import mining claims** with spatial coordinates
- **Populate interactive maps** with real geological data
- **Manage geospatial data** directly in the admin panel

---

## Getting Started

### Accessing the Import Interface

1. **Log in** as an administrator
2. Navigate to **Admin Dashboard** → **QGIS Data Import** tab
3. Or go directly to: `/admin/geospatial`

### File Formats Supported

| Format | Description | Use Case |
|--------|-------------|----------|
| **GeoJSON** | Standard web-based geospatial format | Recommended for complex geometries |
| **CSV** | Comma-separated values | Simple, tabular data |
| **JSON** | JavaScript Object Notation | Alternative to GeoJSON |

---

## Exporting from QGIS

### Export as GeoJSON

1. **Open your QGIS project** with mineral deposits or mining claims layer
2. **Right-click** on the layer in the Layers Panel
3. Select **Export As** → **GeoJSON**
4. Configure export options:
   - **Format:** GeoJSON
   - **CRS:** Keep as is (or use EPSG:4326 for WGS84)
   - **Filename:** e.g., `deposits.geojson`
5. Click **OK** to save

### Export as CSV

1. **Right-click** on the layer
2. Select **Export As** → **Comma Separated Values [CSV]**
3. Configure settings:
   - **Include geometry:** YES (if available) or add lat/lon as separate columns
4. Ensure your CSV has these columns:
   - For **Deposits:** name, latitude, longitude, country, region, status, reserves, grade
   - For **Claims:** claim_id, latitude, longitude, company, area_hectares, status

---

## Required Data Fields

### For Mineral Deposits

**Required Fields:**
```
Name of the deposit
Latitude (decimal degrees, -90 to 90)
Longitude (decimal degrees, -180 to 180)
```

**Optional Fields:**
```
location_name    - Specific location within country
country          - Country name
region           - Province/region name
status           - Active, Prospect, or Historical
reserves         - Estimated reserves (tonnes)
grade            - Average grade (%)
confidence       - Confidence level of estimate
year             - Discovery year
notes            - Additional notes
```

**Example GeoJSON Feature:**
```json
{
  "type": "Feature",
  "properties": {
    "name": "Jabal Al-Akhdar Gold Deposit",
    "country": "South Sudan",
    "region": "Eastern Equatoria",
    "status": "Active",
    "reserves": 2500000,
    "grade": 2.8,
    "confidence": "High",
    "year": 2005
  },
  "geometry": {
    "type": "Point",
    "coordinates": [32.5, 15.5]  // [longitude, latitude]
  }
}
```

### For Mining Claims

**Required Fields:**
```
Claim ID (unique identifier)
Latitude (decimal degrees)
Longitude (decimal degrees)
```

**Optional Fields:**
```
company          - Company holding the claim
location         - Location description
area_hectares    - Area of the claim
claim_type       - Exploration, Mining, etc.
status           - Active, Inactive, Expired
```

**Example CSV Row:**
```
CLM-2024-001,15.5,32.5,Nile Gold Resources,5000,Active,Exploration
```

---

## Step-by-Step Import Process

### 1. Prepare Your Data in QGIS

- **Verify coordinates:** Ensure latitude/longitude are in decimal degrees (WGS84)
- **Check field names:** Equipment them closely (case-insensitive)
- **Remove duplicates:** Check for duplicate entries before export
- **Validate geometry:** Ensure all features have valid coordinates

### 2. Export from QGIS

- Follow the export instructions above
- Save file to your computer
- Verifyfile is readable

### 3. Access the Import Page

```
URL: http://localhost:5000/admin/geospatial
```

### 4. Upload Your File

**For Deposits:**
1. Click the **Deposits** tab
2. Click **"Choose File"** and select your GeoJSON or CSV
3. (Optional) Select a specific mineral type, or leave as "Auto-detect"
4. Click **"Import Deposits"**

**For Claims:**
1. Click the **Claims** tab
2. Click **"Choose File"** and select your GeoJSON or CSV
3. Click **"Import Claims"**

### 5. Review Results

The system will show:
- ✅ **Inserted:** Number of new records added
- ⚠️ **Duplicates:** Records skipped (same name and location)
- **Total:** Total records in file

### 6. View on Map

- Go to **Maps** → **Deposit Maps** or **Claims Maps**
- Your imported data will appear as markers
- Click markers for details

---

## Data Validation Rules

### Latitude/Longitude Validation
```
Latitude:  -90 to +90 degrees
Longitude: -180 to +180 degrees
```

### Duplicate Detection
- **Deposits:** Same name + same location (lat/lng) = duplicate
- **Claims:** Same claim_id = duplicate

### Status Values Accepted
```
Deposits: Active, Prospect, Historical, Exploration
Claims:   Active, Inactive, Expired, Suspended
```

---

## Troubleshooting

### "Invalid GeoJSON Format"
- ✓ Verify JSON structure: `{  "type": "FeatureCollection", "features": [ ... ] }`
- ✓ Use online GeoJSON validator: [geojson.io](https://geojson.io)
- ✓ Check for special characters in field names

### "No valid data found in file"
- ✓ Ensure Feature.geometry.coordinates has [longitude,  latitude]
- ✓ Verify latitude/longitude are numeric (not text)
- ✓ Check for missing coordinates (required fields)

### "Column not found"
- ✓ Check CSV header spellings (case-insensitive)
- ✓ Ensure columns are comma-separated
- ✓ Verify no extra whitespace in column names

### "Import failed" Error
- ✓ Check file size (max ~50MB recommended)
- ✓ Verify file permissions
- ✓ Try reparsing with online tools first
- ✓ Check server logs: `tail -20 /tmp/flask.log`

---

## API Endpoints

### Import Deposits
```
POST /admin/geospatial/import-deposits
Content-Type: multipart/form-data

Parameters:
- file: GeoJSON or CSV file
- mineral_type_id: (optional) Mineral type ID
```

**Response:**
```json
{
  "success": true,
  "message": "Imported 5 deposits",
  "inserted": 5,
  "duplicates": 2,
  "total": 7
}
```

### Import Claims
```
POST /admin/geospatial/import-claims
Content-Type: multipart/form-data

Parameters:
- file: GeoJSON or CSV file
```

### Clear All Deposits
```
POST /admin/geospatial/clear-deposits
```

### Clear All Claims
```
POST /admin/geospatial/clear-claims

⚠️ WARNING: This action is irreversible
```

---

## Sample Files

Sample GeoJSON and CSV files are included in the `samples/` directory:

```
samples/
├── sample_deposits.geojson    # Example mineral deposits
└── sample_claims.csv           # Example mining claims
```

### Quick Start with Samples

1. Go to `/admin/geospatial`
2. Click **"Download CSV Template"** for reference format
3. Use the sample files as a template
4. Modify with your actual data
5. Upload to import

---

## Best Practices

### Data Preparation

1. **Validate Coordinates**
   ```
   Check: -90 < lat < 90
   Check: -180 < lng < 180
   ```

2. **Clean Field Names**
   ```
   Use: name, latitude, longitude
   Not: Name*, latitude (degrees), lng
   ```

3. **Standardize Status Values**
   ```
   Use consistent values across files
   E.g.: "Active" not "active" or "ACTIVE"
   ```

4. **Remove Duplicates Before Import**
   ```
   Use QGIS → Vector → Geoprocessing Tools → 
   "Remove Duplicates"
   ```

5. **Handle NULL Values**
   ```
   Blank cells are okay for optional fields
   Use "N/A" or leave empty for missing data
   ```

### Workflow

1. **Prepare layer in QGIS**
2. **Filter & validate data**
3. **Export to GeoJSON/CSV**
4. **Test import on sample** (optional)
5. **Upload full dataset**
6. **Verify on map**
7. **Backup database** regularly

---

## Performance Considerations

- **File Size:** Optimal <500 records for smooth import
- **Coordinates:** Use decimal degrees (efficient storage)
- **Batch Imports:** Can import multiple files sequentially
- **Update Strategy:** Clear old data before importing new dataset

---

## Map Display

### After Import

**Deposits Map** (`/map/deposits`)
- Shows all imported deposits as markers
- Color-coded by status (Active/Prospect/Historical)
- Click for details
- Filter by mineral type

**Claims Map** (`/map/claims`)
- Shows all imported claims as markers
- Approximate circles representing claim area
- Click for company and status info
- Filter by status

---

## Integration with QGIS Workflows

### Workflow 1: Regular Data Updates

```
1. Update layer in QGIS
   ↓
2. Export to GeoJSON
   ↓
3. Import to GeoResource Explorer
   ↓
4. View on map
   ↓
5. Share with stakeholders
```

### Workflow 2: Multi-Source Data Merge

```
1. Collect data from multiple QGIS projects
   ↓
2. Merge into single layer in QGIS
   ↓
3. Remove duplicates
   ↓
4. Export and import
```

### Workflow 3: Continuous Monitoring

```
1. Maintain live QGIS project
   ↓
2. Schedule weekly/monthly exports
   ↓
3. Automated import via API
   ↓
4. Track changes over time
```

---

## FAQ

**Q: Can I import Shapefiles directly?**
A: Currently, export from QGIS as GeoJSON first, then import.

**Q: What happens to existing data when I import?**
A: Duplicates are skipped. Existing data is preserved.

**Q: Can I update existing deposits?**
A: Not directly. Clear old data and re-import, or manually edit in admin panel.

**Q: How many records can I import at once?**
A: No hard limit, but recommend <1000 per file for best performance.

**Q: Are my coordinates private?**
A: Maps are only visible to logged-in users. Configure in Admin Panel.

**Q: Can I export data back to QGIS?**
A: Yes, use Download CSV on the map pages, then import to QGIS.

---

## Advanced Usage

### CSV with GeoJSON Geometry

You can include GeoJSON geometry in CSV:

```csv
name,latitude,longitude,country,geometry_json
"Site A",15.5,32.5,"South Sudan","{""type"":""Point"",""coordinates"":[32.5,15.5]}"
```

### Bulk Import via API

Use cURL to import from command line:

```bash
curl -X POST http://localhost:5000/admin/geospatial/import-deposits \
  -F "file=@deposits.geojson" \
  -F "mineral_type_id=1"
```

### Scheduled Imports

Set up cron job to import updated data:

```bash
# Weekly import
0 2 * * 0 curl -X POST http://localhost:5000/admin/geospatial/import-deposits \
  -F "file=@/path/to/deposits.geojson"
```

---

## Support & Resources

- **QGIS Documentation:** [qgis.org/en/docs](https://qgis.org/en/docs)
- **GeoJSON Spec:** [geojson.org](https://geojson.org)
- **CSV Format:** [RFC 4180](https://tools.ietf.org/html/rfc4180)
- **Coordinate System:** [EPSG:4326](https://epsg.io/4326)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-06 | 1.0 | Initial QGIS import feature release |

---

**Last Updated:** February 6, 2026  
**Feature Status:** ✅ Production Ready
