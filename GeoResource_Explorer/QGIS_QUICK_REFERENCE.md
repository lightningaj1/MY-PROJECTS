# QGIS Import Quick Reference Card

## 📌 5-Minute Quickstart

### Step 1: Export from QGIS
```
Right-click on layer → Export As → GeoJSON
(or CSV with latitude/longitude columns)
```

### Step 2: Access Import Page
```
URL: http://localhost:5000/admin/geospatial
(must be logged in as admin)
```

### Step 3: Upload File
- Click **Deposits** or **Claims** tab
- Select your GeoJSON/CSV file
- Click **Import**

### Step 4: View on Map
```
Maps → Deposits Map (or Claims Map)
```

---

## 📋 Required Fields Reference

### Mineral Deposits (Minimum)
```
✓ name          (string)
✓ latitude      (number: -90 to 90)
✓ longitude     (number: -180 to 180)
```

### Mining Claims (Minimum)
```
✓ claim_id      (string, unique)
✓ latitude      (number: -90 to 90)
✓ longitude     (number: -180 to 180)
```

---

## 📁 File Format Examples

### GeoJSON Template
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "My Deposit",
        "latitude": 15.5,
        "longitude": 32.5,
        "country": "South Sudan",
        "status": "Active"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [32.5, 15.5]  // [lon, lat]
      }
    }
  ]
}
```

### CSV Template
```
name,latitude,longitude,country,status
"My Deposit",15.5,32.5,"South Sudan","Active"
"Prospect Site",14.2,31.8,"South Sudan","Prospect"
```

---

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Invalid GeoJSON" | Validate at [geojson.io](https://geojson.io) |
| "No data found" | Check lat/lon are numbers, not text |
| "Coordinates error" | Verify: -90<lat<90 and -180<lon<180 |
| "Column not found" | Check CSV headers match expected names |
| File won't upload | Verify file extension (.geojson or .csv) |

---

## 🎓 Important Reminders

1. **Coordinates must be:**
   - Decimal degrees (not degrees/minutes/seconds)
   - WGS84 projection (EPSG:4326)
   
2. **Latitude/Longitude order:**
   - **CSV:** Use columns named `latitude` and `longitude`
   - **GeoJSON geometry:** Use `[longitude, latitude]` format

3. **Status values:**
   - Deposits: `Active`, `Prospect`, `Historical`
   - Claims: `Active`, `Inactive`, `Expired`

4. **Duplicates:**
   - System automatically skips duplicate entries
   - Deposits: Same name + location = duplicate
   - Claims: Same claim_id = duplicate

---

## 🔗 Admin Pages

| Page | URL | Purpose |
|------|-----|---------|
| Import Deposits | `/admin/geospatial` (tab: Deposits) | Upload GeoJSON/CSV |
| Import Claims | `/admin/geospatial` (tab: Claims) | Upload mining claims |
| View Deposits | `/map/deposits` | Interactive deposits map |
| View Claims | `/map/claims` | Interactive claims map |

---

## 💡 Pro Tips

✅ **Validate Before Import**
- Use [geojson.io](https://geojson.io) to preview GeoJSON
- Check CSV in spreadsheet app
- Remove duplicates in QGIS first

✅ **Organize Your Data**
- One feature type per file (deposits OR claims, not mixed)
- Use meaningful names
- Include optional fields for richer data

✅ **Keep Backups**
- Export maps regularly
- Keep original QGIS projects
- Archive imports with dates

✅ **Use Samples**
- Check `samples/sample_deposits.geojson`
- Check `samples/sample_claims.csv`
- Use as templates for your data

---

## 📞 Need Help?

- **Full Guide:** See [QGIS_IMPORT_GUIDE.md](../QGIS_IMPORT_GUIDE.md)
- **Sample Files:** Check `samples/` directory
- **QGIS Help:** [qgis.org/en/docs](https://qgis.org/en/docs)
- **GeoJSON Spec:** [geojson.org](https://geojson.org)

---

## ✨ What Happens After Import

```
Your Data
    ↓
Upload GeoJSON/CSV
    ↓
System Validates & Parses
    ↓
Check for Duplicates
    ↓
Insert into Database
    ↓
Update Maps Automatically
    ↓
Share with Team!
```

---

**Print this card** and keep it handy while working with QGIS!

**Last Updated:** February 6, 2026
