"""
Geospatial Data Management & QGIS Import
Handles GeoJSON, Shapefile, and CSV data import from QGIS
"""

import json
import csv
import io
from flask import render_template, request, jsonify, redirect, session
from werkzeug.utils import secure_filename
from app.db import get_db
from app.utils import is_admin
from app.helpers import login_required
import zipfile

# Allowed file types for QGIS imports
ALLOWED_GIS_EXTENSIONS = {'json', 'geojson', 'csv', 'zip', 'shp', 'dbf', 'shx'}

def allowed_gis_file(filename):
    """Check if file is a valid GIS format"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_GIS_EXTENSIONS

def parse_geojson_features(features, data_type='deposits'):
    """
    Parse GeoJSON FeatureCollection and extract relevant data
    
    Args:
        features: List of GeoJSON features
        data_type: 'deposits' or 'claims'
    
    Returns:
        List of parsed data dicts
    """
    parsed_data = []
    
    for feature in features:
        if feature.get('type') != 'Feature':
            continue
            
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        if geom.get('type') == 'Point':
            coords = geom.get('coordinates', [])
            if len(coords) >= 2:
                lng, lat = coords[0], coords[1]
                
                if data_type == 'deposits':
                    parsed_data.append({
                        'name': props.get('name', props.get('NAME', 'Unknown Deposit')),
                        'mineral_type_id': 1,  # Default - user can update later
                        'ore_type_id': 1,  # Default - user can update later
                        'location_name': props.get('location', props.get('LOCATION', '')),
                        'latitude': lat,
                        'longitude': lng,
                        'country': props.get('country', props.get('COUNTRY', '')),
                        'region': props.get('region', props.get('REGION', '')),
                        'estimated_reserves_tonnes': float(props.get('reserves', props.get('RESERVES', 0))) if props.get('reserves') or props.get('RESERVES') else None,
                        'average_grade': float(props.get('grade', props.get('GRADE', 0))) if props.get('grade') or props.get('GRADE') else None,
                        'confidence_level': props.get('confidence', props.get('CONFIDENCE', 'Unknown')),
                        'discovery_year': int(props.get('year', props.get('YEAR', 0))) if props.get('year') or props.get('YEAR') else None,
                        'status': props.get('status', props.get('STATUS', 'Prospect')),
                        'notes': props.get('notes', props.get('NOTES', '')),
                    })
                    
                elif data_type == 'claims':
                    parsed_data.append({
                        'claim_id': props.get('claim_id', props.get('CLAIM_ID', 'CLM-' + str(len(parsed_data)))),
                        'company_name': props.get('company', props.get('COMPANY', '')),
                        'location_description': props.get('location', props.get('LOCATION', '')),
                        'area_hectares': float(props.get('area', props.get('AREA', 0))) if props.get('area') or props.get('AREA') else None,
                        'claim_type': props.get('claim_type', props.get('CLAIM_TYPE', 'Exploration')),
                        'latitude': lat,
                        'longitude': lng,
                        'status': props.get('status', props.get('STATUS', 'Active')),
                    })
    
    return parsed_data

def parse_csv_data(csv_content, data_type='deposits'):
    """
    Parse CSV data from QGIS export
    Expected columns: name, latitude, longitude, [other fields based on type]
    
    Args:
        csv_content: String content of CSV file
        data_type: 'deposits' or 'claims'
    
    Returns:
        List of parsed data dicts
    """
    parsed_data = []
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        try:
            lat = float(row.get('latitude', row.get('Latitude', row.get('LAT', 0))))
            lng = float(row.get('longitude', row.get('Longitude', row.get('LON', 0))))
            
            if lat == 0 and lng == 0:
                continue
                
            if data_type == 'deposits':
                parsed_data.append({
                    'name': row.get('name', row.get('Name', row.get('NAME', 'Unknown'))),
                    'mineral_type_id': 1,  # Default
                    'ore_type_id': 1,  # Default
                    'location_name': row.get('location', row.get('Location', '')),
                    'latitude': lat,
                    'longitude': lng,
                    'country': row.get('country', row.get('Country', '')),
                    'region': row.get('region', row.get('Region', '')),
                    'estimated_reserves_tonnes': float(row.get('reserves', row.get('Reserves', 0))) if row.get('reserves') or row.get('Reserves') else None,
                    'average_grade': float(row.get('grade', row.get('Grade', 0))) if row.get('grade') or row.get('Grade') else None,
                    'confidence_level': row.get('confidence', row.get('Confidence', 'Unknown')),
                    'discovery_year': int(row.get('year', row.get('Year', 0))) if row.get('year') or row.get('Year') else None,
                    'status': row.get('status', row.get('Status', 'Prospect')),
                    'notes': row.get('notes', row.get('Notes', '')),
                })
                
            elif data_type == 'claims':
                parsed_data.append({
                    'claim_id': row.get('claim_id', row.get('Claim_ID', row.get('CLAIM_ID', f'CLM-{len(parsed_data)}'))),
                    'company_name': row.get('company', row.get('Company', '')),
                    'location_description': row.get('location', row.get('Location', '')),
                    'area_hectares': float(row.get('area', row.get('Area', 0))) if row.get('area') or row.get('Area') else None,
                    'claim_type': row.get('claim_type', row.get('Claim_Type', 'Exploration')),
                    'latitude': lat,
                    'longitude': lng,
                    'status': row.get('status', row.get('Status', 'Active')),
                })
        except (ValueError, KeyError):
            continue
    
    return parsed_data

def geospatial_routes(app):
    """Register geospatial/QGIS import routes"""
    
    @app.route("/admin/geospatial")
    @login_required
    def geospatial_admin():
        """Admin page for geospatial data management"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        # Get current data counts
        deposits_count = db.execute("SELECT COUNT(*) as count FROM deposits").fetchone()['count']
        claims_count = db.execute("SELECT COUNT(*) as count FROM mining_claims").fetchone()['count']
        
        # Get mineral types for reference
        mineral_types = db.execute("SELECT id, name FROM mineral_types ORDER BY name").fetchall()
        mineral_types = [dict(m) for m in mineral_types]
        
        return render_template(
            "geospatial_admin.html",
            deposits_count=deposits_count,
            claims_count=claims_count,
            mineral_types=mineral_types
        )
    
    @app.route("/admin/geospatial/import-deposits", methods=["POST"])
    @login_required
    def import_deposits():
        """Import mineral deposits from QGIS GeoJSON or CSV"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_gis_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use GeoJSON, CSV, or Shapefile'}), 400
        
        try:
            filename = secure_filename(file.filename).lower()
            
            if filename.endswith(('.geojson', '.json')):
                # Parse GeoJSON
                content = file.read().decode('utf-8')
                geojson_data = json.loads(content)
                features = geojson_data.get('features', [])
                parsed_deposits = parse_geojson_features(features, 'deposits')
                
            elif filename.endswith('.csv'):
                # Parse CSV
                content = file.read().decode('utf-8')
                parsed_deposits = parse_csv_data(content, 'deposits')
                
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
            
            if not parsed_deposits:
                return jsonify({'error': 'No valid data found in file'}), 400
            
            # Get mineral type ID from form if provided
            mineral_type_id = request.form.get('mineral_type_id', 1, type=int)
            
            # Insert deposits into database
            db = get_db()
            inserted = 0
            duplicates = 0
            
            for deposit in parsed_deposits:
                # Check for duplicate (same name and location)
                existing = db.execute(
                    "SELECT id FROM deposits WHERE name = ? AND latitude = ? AND longitude = ?",
                    (deposit['name'], deposit['latitude'], deposit['longitude'])
                ).fetchone()
                
                if existing:
                    duplicates += 1
                    continue
                
                # Update mineral type if provided
                deposit['mineral_type_id'] = mineral_type_id
                
                db.execute(
                    """INSERT INTO deposits 
                    (name, mineral_type_id, ore_type_id, location_name, latitude, longitude, 
                     country, region, estimated_reserves_tonnes, average_grade, confidence_level, 
                     discovery_year, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (deposit['name'], deposit['mineral_type_id'], deposit['ore_type_id'],
                     deposit['location_name'], deposit['latitude'], deposit['longitude'],
                     deposit['country'], deposit['region'], deposit['estimated_reserves_tonnes'],
                     deposit['average_grade'], deposit['confidence_level'], deposit['discovery_year'],
                     deposit['status'], deposit['notes'])
                )
                inserted += 1
            
            db.commit()
            
            return jsonify({
                'success': True,
                'message': f'Imported {inserted} deposits',
                'inserted': inserted,
                'duplicates': duplicates,
                'total': len(parsed_deposits)
            }), 200
        
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid GeoJSON format'}), 400
        except Exception as e:
            return jsonify({'error': f'Import failed: {str(e)}'}), 500
    
    @app.route("/admin/geospatial/import-claims", methods=["POST"])
    @login_required
    def import_claims():
        """Import mining claims from QGIS GeoJSON or CSV"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_gis_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use GeoJSON or CSV'}), 400
        
        try:
            filename = secure_filename(file.filename).lower()
            
            if filename.endswith(('.geojson', '.json')):
                # Parse GeoJSON
                content = file.read().decode('utf-8')
                geojson_data = json.loads(content)
                features = geojson_data.get('features', [])
                parsed_claims = parse_geojson_features(features, 'claims')
                
            elif filename.endswith('.csv'):
                # Parse CSV
                content = file.read().decode('utf-8')
                parsed_claims = parse_csv_data(content, 'claims')
                
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
            
            if not parsed_claims:
                return jsonify({'error': 'No valid data found in file'}), 400
            
            # Insert claims into database
            db = get_db()
            inserted = 0
            duplicates = 0
            
            for claim in parsed_claims:
                # Check for duplicate (same claim_id)
                existing = db.execute(
                    "SELECT id FROM mining_claims WHERE claim_id = ?",
                    (claim['claim_id'],)
                ).fetchone()
                
                if existing:
                    duplicates += 1
                    continue
                
                db.execute(
                    """INSERT INTO mining_claims 
                    (claim_id, company_name, location_description, area_hectares, 
                     claim_type, latitude, longitude, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (claim['claim_id'], claim['company_name'], claim['location_description'],
                     claim['area_hectares'], claim['claim_type'], claim['latitude'],
                     claim['longitude'], claim['status'])
                )
                inserted += 1
            
            db.commit()
            
            return jsonify({
                'success': True,
                'message': f'Imported {inserted} claims',
                'inserted': inserted,
                'duplicates': duplicates,
                'total': len(parsed_claims)
            }), 200
        
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid GeoJSON format'}), 400
        except Exception as e:
            return jsonify({'error': f'Import failed: {str(e)}'}), 500
    
    @app.route("/admin/geospatial/clear-deposits", methods=["POST"])
    @login_required
    def clear_deposits():
        """Clear all deposits from database"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        db.execute("DELETE FROM deposits")
        db.commit()
        
        return jsonify({'success': True, 'message': 'All deposits cleared'}), 200
    
    @app.route("/admin/geospatial/clear-claims", methods=["POST"])
    @login_required
    def clear_claims():
        """Clear all mining claims from database"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        db.execute("DELETE FROM mining_claims")
        db.commit()
        
        return jsonify({'success': True, 'message': 'All claims cleared'}), 200
