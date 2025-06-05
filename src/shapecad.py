# -*- coding: utf-8 -*-

__version__ = "2.1.0"
__author__ = "Daniel Adi Nugroho"
__email__ = "dnugroho@gmail.com"
__status__ = "Production"
__date__ = "2025-06-04"
__copyright__ = "Copyright (c) 2025 Daniel Adi Nugroho"
__license__ = "GNU General Public License v3.0 (GPL-3.0)"

# Version History
# --------------

# 2.1.0 (2025-06-04)
# - Automatic geometry type detection for SHP → DXF conversion
# - Coordinate Reference System (CRS) detection and display
# - Australian datum support (GDA1994, GDA2020) with MGA zone detection
# - Real-time shapefile analysis with CRS information
# - Enhanced user interface with detailed coordinate system feedback
# - Improved error handling and validation

# 2.0.0 (2025-06-03)
# - Complete rewrite with enhanced geometry detection
# - Added support for Australian coordinate systems
# - Improved DXF entity handling (POINT, LINE, LWPOLYLINE, POLYLINE, CIRCLE)
# - Enhanced shapefile analysis capabilities
# - Better error handling and logging

# 1.0.1 (2023-10-25)
# - Added warning text on the tool's capabilities and limitations
# - Added support for reading coordinate system from Shapefile (PRJ file)
# - Added support for reading projection information from DXF file header
# - Warns the user if no projection information is found in the DXF file
# - Attempts to save projection information as extended data (XDATA) in the DXF file

# 1.0.0 (2023-10-25)
# - Initial release
# - Support for SHP to DXF and DXF to SHP conversions
# - Wizard-style GUI with Tkinter
# - Support for multiple DXF versions (R2010, R2013, R2018)
# - Coordinate system options: MGA1994 and MGA2020
# - MGA zone selection (50 to 56)
# - Feature type selection (Point, Line, Polygon)
# - Preserves elevation (Z values) in 3D data

"""
SHP ↔ DXF Converter
==================

A graphical user interface for converting between ESRI Shapefile and AutoCAD DXF formats,
with specialized support for Australian coordinate systems and automatic geometry detection.

Purpose:
--------
- Provide bidirectional conversion between SHP and DXF formats
- Support Australian coordinate reference systems (GDA1994, GDA2020 MGA)
- Automatically detect geometry types and coordinate systems
- Handle multiple geometry types (Points, Lines, Polygons/Areas)
- Provide real-time feedback on shapefile analysis

Requirements:
------------
- Python 3.10 or higher
- Required packages:
  - tkinter: for GUI components
  - geopandas: for spatial data handling
  - ezdxf: for DXF file processing
  - shapely: for geometry operations
  - logging: for error tracking and debugging
  - pathlib: for path handling
  - threading: for non-blocking operations

Features:
---------
1. DXF to Shapefile Conversion:
   - Support for DXF entity types: POINT, LINE, LWPOLYLINE, POLYLINE, CIRCLE
   - Australian coordinate system assignment (GDA1994/GDA2020 MGA)
   - Zone selection for MGA projections (Zones 50-56)
   - Entity type filtering during conversion

2. Shapefile to DXF Conversion:
   - Automatic geometry type detection from shapefile
   - Real-time coordinate reference system analysis
   - Australian CRS recognition and validation
   - Support for Point, LineString, and Polygon geometries
   - Binary and ASCII DXF output formats

3. Coordinate System Support:
   - GDA1994 MGA Zones 50-56 (EPSG:28350-28356)
   - GDA2020 MGA Zones 50-56 (EPSG:7850-7856)
   - Geographic coordinate systems (EPSG:4283, EPSG:7844)
   - Non-Australian CRS detection with warnings

4. User Interface:
   - Tabbed interface for different conversion directions
   - Real-time shapefile analysis and CRS detection
   - Progress indicators during conversion
   - Comprehensive help and about information
   - Detailed error messages and logging

Usage:
------
1. Launch the application:
   python shapecad4.py

2. DXF to Shapefile:
   - Select input DXF file
   - Choose output shapefile location
   - Set coordinate system (datum and MGA zone)
   - Select entity type to convert
   - Execute conversion

3. Shapefile to DXF:
   - Select input shapefile (automatic analysis will begin)
   - Review detected geometry type and coordinate system
   - Choose output DXF file location
   - Set DXF format options
   - Execute conversion

Supported Entity Types:
----------------------
- Points: DXF POINT entities ↔ SHP Point/MultiPoint geometries
- Lines: DXF LINE/LWPOLYLINE (open) ↔ SHP LineString/MultiLineString geometries
- Polygons/Areas: DXF LWPOLYLINE (closed)/CIRCLE ↔ SHP Polygon/MultiPolygon geometries

Australian MGA Zone Coverage:
----------------------------
- Zone 50: Western Australia (west)    - Zone 54: Northern Territory, Queensland
- Zone 51: Western Australia (east)    - Zone 55: New South Wales, Victoria, Tasmania
- Zone 52: South Australia (west)      - Zone 56: New South Wales, Queensland (east)
- Zone 53: South Australia (east)

Technical Notes:
---------------
- DXF files do not contain coordinate reference system information
- Always document the coordinate system used when sharing DXF files
- Log files are created with pattern: converter_YYYYMMDD.log
- All operations are performed in separate threads to prevent UI freezing
- Comprehensive error handling and user feedback throughout

GNU GENERAL PUBLIC LICENSE
--------------------------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

# Core imports
print("Core imports starts.")
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
print("Tkinter imports finished.")
import os, sys, datetime, threading, logging
import platform, subprocess, datetime
print("System imports finished.")
from pathlib import Path
print("Pathlib imports finished.")
from datetime import datetime

# Geospatial processing imports
print("Geospatial imports starts.")
import geopandas as gpd
import ezdxf
from shapely.geometry import Point, LineString, Polygon
print("Geospatial imports finished.")
print("All imports finished.")


# Configure enhanced logging with timestamp and better formatting
def setup_logging():
    """Set up logging configuration with rotating file handler"""
    log_filename = f"converter_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console for debugging
        ]
    )

# Setup logging when module is imported
setup_logging()

# Constants - organized and documented
class Config:
    """Configuration constants for the converter application"""
    
    # EPSG codes for Australian coordinate systems
    GDA1994_BASE_EPSG = 28300  # Base EPSG code for GDA1994 MGA zones
    GDA2020_BASE_EPSG = 7800   # Base EPSG code for GDA2020 MGA zones
    
    # Supported MGA zones for Australia
    SUPPORTED_ZONES = ["50", "51", "52", "53", "54", "55", "56"]
    
    # Entity types that can be converted
    SUPPORTED_ENTITY_TYPES = ["Points", "Lines", "Polygons/Areas"]
    
    # DXF versions supported by ezdxf
    SUPPORTED_DXF_VERSIONS = ["R2010", "R2013", "R2018", "R2021"]
    
    # Application metadata
    APP_VERSION = "2.1"
    APP_TITLE = "SHP ↔ DXF Converter"
    
    # File type filters for dialogs
    DXF_FILETYPES = [("DXF files", "*.dxf"), ("All files", "*.*")]
    SHP_FILETYPES = [("SHP files", "*.shp"), ("All files", "*.*")]

class FileValidator:
    """Utility class for file validation and path handling"""
    
    @staticmethod
    def validate_file_exists(filepath):
        """Check if file exists and is readable"""
        if not filepath:
            return False, "No file path provided"
        
        path = Path(filepath)
        if not path.exists():
            return False, f"File does not exist: {filepath}"
        
        if not path.is_file():
            return False, f"Path is not a file: {filepath}"
        
        try:
            # Try to open file to check if it's readable
            with open(filepath, 'rb') as f:
                pass
            return True, "File is valid"
        except PermissionError:
            return False, f"Permission denied accessing file: {filepath}"
        except Exception as e:
            return False, f"Error accessing file: {str(e)}"
    
    @staticmethod
    def validate_output_path(filepath):
        """Validate output file path and directory permissions"""
        if not filepath:
            return False, "No output path provided"
        
        path = Path(filepath)
        parent_dir = path.parent
        
        # Check if parent directory exists and is writable
        if not parent_dir.exists():
            return False, f"Output directory does not exist: {parent_dir}"
        
        if not os.access(parent_dir, os.W_OK):
            return False, f"No write permission for directory: {parent_dir}"
        
        return True, "Output path is valid"
    
    @staticmethod
    def validate_file_extension(filepath, expected_ext):
        """Validate file has correct extension"""
        if not filepath:
            return False, f"No file path provided"
        
        path = Path(filepath)
        if path.suffix.lower() != expected_ext.lower():
            return False, f"File must have {expected_ext} extension"
        
        return True, "File extension is correct"

class GeometryDetector:
    """Class responsible for detecting geometry types and CRS information in shapefiles"""
    
    @staticmethod
    def detect_shapefile_info(shp_path):
        """
        Detect geometry type and CRS information from a shapefile
        
        Args:
            shp_path: Path to the shapefile
            
        Returns:
            dict: {
                'geometry_type': str or None,
                'readable_name': str,
                'feature_count': int,
                'crs_info': dict or None,
                'error': str or None
            }
        """
        result = {
            'geometry_type': None,
            'readable_name': 'Unknown',
            'feature_count': 0,
            'crs_info': None,
            'error': None
        }
        
        try:
            # Read the shapefile to examine geometry types and CRS
            gdf = gpd.read_file(shp_path)
            
            if gdf.empty:
                result['error'] = "Shapefile contains no geometries"
                return result
            
            # Detect geometry type
            geometry_counts = {}
            total_valid = 0
            
            for geom in gdf.geometry:
                if geom is not None and not geom.is_empty:
                    geom_type = geom.geom_type
                    geometry_counts[geom_type] = geometry_counts.get(geom_type, 0) + 1
                    total_valid += 1
            
            if total_valid == 0:
                result['error'] = "Shapefile contains no valid geometries"
                return result
            
            # Find the most common geometry type
            primary_geom_type = max(geometry_counts, key=geometry_counts.get)
            primary_count = geometry_counts[primary_geom_type]
            
            # Map geometry types to our entity types
            geom_type_mapping = {
                'Point': ('Point', 'Points'),
                'MultiPoint': ('Point', 'Points'),
                'LineString': ('LineString', 'Lines'),
                'MultiLineString': ('LineString', 'Lines'),
                'Polygon': ('Polygon', 'Polygons/Areas'),
                'MultiPolygon': ('Polygon', 'Polygons/Areas')
            }
            
            if primary_geom_type in geom_type_mapping:
                shapely_type, readable_name = geom_type_mapping[primary_geom_type]
                result['geometry_type'] = shapely_type
                result['readable_name'] = readable_name
                result['feature_count'] = primary_count
                
                logging.info(f"Detected geometry type in {shp_path}: {primary_geom_type} "
                           f"({primary_count}/{total_valid} geometries)")
                
                # Log if there are mixed geometry types (should be rare for valid shapefiles)
                if len(geometry_counts) > 1:
                    logging.warning(f"Mixed geometry types detected: {geometry_counts}")
            else:
                result['error'] = f"Unsupported geometry type: {primary_geom_type}"
                return result
            
            # Detect CRS information
            result['crs_info'] = GeometryDetector.detect_australian_crs(gdf.crs)
            
            return result
                
        except Exception as e:
            logging.error(f"Error analyzing shapefile {shp_path}: {str(e)}")
            result['error'] = f"Error reading shapefile: {str(e)}"
            return result
    
    @staticmethod
    def detect_australian_crs(crs):
        """
        Detect Australian CRS information from a CRS object
        
        Args:
            crs: CRS object from geopandas
            
        Returns:
            dict: {
                'datum': str,
                'projection': str,
                'zone': str,
                'epsg_code': int or None,
                'is_australian': bool,
                'crs_string': str
            } or None if no CRS
        """
        if crs is None:
            return None
        
        crs_info = {
            'datum': 'Unknown',
            'projection': 'Unknown',
            'zone': 'Unknown',
            'epsg_code': None,
            'is_australian': False,
            'crs_string': str(crs)
        }
        
        try:
            # Get EPSG code if available
            if hasattr(crs, 'to_epsg') and crs.to_epsg():
                crs_info['epsg_code'] = crs.to_epsg()
                epsg_code = crs_info['epsg_code']
                
                # Check for Australian GDA1994 MGA zones (EPSG 283xx)
                if 28350 <= epsg_code <= 28356:
                    crs_info['datum'] = 'GDA1994'
                    crs_info['projection'] = 'MGA'
                    crs_info['zone'] = str(epsg_code - 28300)
                    crs_info['is_australian'] = True
                
                # Check for Australian GDA2020 MGA zones (EPSG 785x)
                elif 7850 <= epsg_code <= 7856:
                    crs_info['datum'] = 'GDA2020'
                    crs_info['projection'] = 'MGA'
                    crs_info['zone'] = str(epsg_code - 7800)
                    crs_info['is_australian'] = True
                
                # Check for some other common Australian systems
                elif epsg_code == 4283:
                    crs_info['datum'] = 'GDA1994'
                    crs_info['projection'] = 'Geographic (Lat/Lon)'
                    crs_info['zone'] = 'N/A'
                    crs_info['is_australian'] = True
                
                elif epsg_code == 7844:
                    crs_info['datum'] = 'GDA2020'
                    crs_info['projection'] = 'Geographic (Lat/Lon)'
                    crs_info['zone'] = 'N/A'
                    crs_info['is_australian'] = True
            
            # If EPSG lookup didn't work, try parsing the CRS string
            if not crs_info['is_australian']:
                crs_string = str(crs).upper()
                
                # Look for GDA1994 indicators
                if 'GDA1994' in crs_string or 'GDA94' in crs_string:
                    crs_info['datum'] = 'GDA1994'
                    crs_info['is_australian'] = True
                    
                    # Look for MGA zone information
                    if 'MGA' in crs_string:
                        crs_info['projection'] = 'MGA'
                        # Try to extract zone number
                        import re
                        zone_match = re.search(r'ZONE[_\s]*(\d{2})', crs_string)
                        if zone_match:
                            crs_info['zone'] = zone_match.group(1)
                
                # Look for GDA2020 indicators
                elif 'GDA2020' in crs_string or 'GDA20' in crs_string:
                    crs_info['datum'] = 'GDA2020'
                    crs_info['is_australian'] = True
                    
                    # Look for MGA zone information
                    if 'MGA' in crs_string:
                        crs_info['projection'] = 'MGA'
                        # Try to extract zone number
                        import re
                        zone_match = re.search(r'ZONE[_\s]*(\d{2})', crs_string)
                        if zone_match:
                            crs_info['zone'] = zone_match.group(1)
            
            logging.info(f"Detected CRS: {crs_info}")
            return crs_info
            
        except Exception as e:
            logging.warning(f"Error parsing CRS information: {str(e)}")
            return crs_info
    
    @staticmethod
    def detect_shapefile_geometry_type(shp_path):
        """
        Legacy method for backward compatibility
        Detect the primary geometry type in a shapefile
        
        Args:
            shp_path: Path to the shapefile
            
        Returns:
            tuple: (geometry_type, readable_name, count) or (None, error_message, 0)
        """
        result = GeometryDetector.detect_shapefile_info(shp_path)
        
        if result['error']:
            return None, result['error'], 0
        else:
            return result['geometry_type'], result['readable_name'], result['feature_count']

class GeometryExtractor:
    """Class responsible for extracting geometries from different file formats"""
    
    @staticmethod
    def extract_from_dxf(msp, entity_type):
        """
        Extract geometries from DXF modelspace based on entity type
        
        Args:
            msp: DXF modelspace object
            entity_type: Type of entities to extract ('Points', 'Lines', 'Polygons/Areas')
        
        Returns:
            List of Shapely geometry objects
        """
        geometries = []
        processed_count = 0
        skipped_count = 0
        entity_type_counts = {}  # Track what entity types we find
        
        logging.info(f"Extracting {entity_type} from DXF file")
        
        # First, let's see what entities are actually in the DXF
        total_entities = 0
        for entity in msp:
            total_entities += 1
            entity_dxf_type = entity.dxftype()
            entity_type_counts[entity_dxf_type] = entity_type_counts.get(entity_dxf_type, 0) + 1
        
        logging.info(f"DXF Analysis: Found {total_entities} total entities")
        logging.info(f"Entity types found: {entity_type_counts}")
        
        # Now process entities based on what we're looking for
        for entity in msp:
            try:
                entity_dxf_type = entity.dxftype()
                
                # Extract Points
                if entity_type == "Points":
                    if entity_dxf_type == 'POINT':
                        # Get X, Y coordinates (ignore Z for 2D shapefile)
                        location = entity.dxf.location
                        point = Point(location.x, location.y)
                        geometries.append(point)
                        processed_count += 1
                        logging.debug(f"Processed POINT at ({location.x}, {location.y})")
                    else:
                        skipped_count += 1
                
                # Extract Lines from various DXF line entities
                elif entity_type == "Lines":
                    if entity_dxf_type == 'LINE':
                        # Simple line entity
                        start = entity.dxf.start
                        end = entity.dxf.end
                        line = LineString([(start.x, start.y), (end.x, end.y)])
                        geometries.append(line)
                        processed_count += 1
                        logging.debug(f"Processed LINE from ({start.x}, {start.y}) to ({end.x}, {end.y})")
                    
                    elif entity_dxf_type == 'LWPOLYLINE':
                        # Check if it's closed or open
                        is_closed = getattr(entity, 'closed', False)
                        if not is_closed:
                            # Open polyline (line)
                            try:
                                points = [(p[0], p[1]) for p in entity.get_points('xy')]
                                if len(points) >= 2:  # Need at least 2 points for a line
                                    line = LineString(points)
                                    geometries.append(line)
                                    processed_count += 1
                                    logging.debug(f"Processed open LWPOLYLINE with {len(points)} points")
                            except Exception as e:
                                logging.warning(f"Error processing LWPOLYLINE: {e}")
                                skipped_count += 1
                        else:
                            skipped_count += 1
                    
                    elif entity_dxf_type == 'POLYLINE':
                        # Legacy polyline entity
                        try:
                            is_closed = getattr(entity, 'is_closed', False)
                            if not is_closed:
                                vertices = list(entity.vertices)
                                if vertices:
                                    points = [(vertex.dxf.location.x, vertex.dxf.location.y) 
                                            for vertex in vertices]
                                    if len(points) >= 2:
                                        line = LineString(points)
                                        geometries.append(line)
                                        processed_count += 1
                                        logging.debug(f"Processed open POLYLINE with {len(points)} points")
                            else:
                                skipped_count += 1
                        except Exception as e:
                            logging.warning(f"Error processing POLYLINE: {e}")
                            skipped_count += 1
                    
                    else:
                        skipped_count += 1
                
                # Extract Polygons/Areas
                elif entity_type == "Polygons/Areas":
                    if entity_dxf_type == 'LWPOLYLINE':
                        # Check if it's closed
                        is_closed = getattr(entity, 'closed', False)
                        if is_closed:
                            try:
                                points = [(p[0], p[1]) for p in entity.get_points('xy')]
                                if len(points) >= 3:  # Need at least 3 points for a polygon
                                    # Close the polygon if last point doesn't equal first
                                    if points[0] != points[-1]:
                                        points.append(points[0])
                                    
                                    polygon = Polygon(points)
                                    if polygon.is_valid:  # Only add valid polygons
                                        geometries.append(polygon)
                                        processed_count += 1
                                        logging.debug(f"Processed closed LWPOLYLINE with {len(points)} points")
                                    else:
                                        skipped_count += 1
                                        logging.warning(f"Invalid polygon skipped: {polygon}")
                            except Exception as e:
                                logging.warning(f"Error processing closed LWPOLYLINE: {e}")
                                skipped_count += 1
                        else:
                            skipped_count += 1
                    
                    elif entity_dxf_type == 'POLYLINE':
                        # Legacy polyline entity
                        try:
                            is_closed = getattr(entity, 'is_closed', False)
                            if is_closed:
                                vertices = list(entity.vertices)
                                if vertices:
                                    points = [(vertex.dxf.location.x, vertex.dxf.location.y) 
                                            for vertex in vertices]
                                    if len(points) >= 3:
                                        # Close the polygon if needed
                                        if points[0] != points[-1]:
                                            points.append(points[0])
                                        
                                        polygon = Polygon(points)
                                        if polygon.is_valid:
                                            geometries.append(polygon)
                                            processed_count += 1
                                            logging.debug(f"Processed closed POLYLINE with {len(points)} points")
                                        else:
                                            skipped_count += 1
                                            logging.warning(f"Invalid polygon from POLYLINE")
                            else:
                                skipped_count += 1
                        except Exception as e:
                            logging.warning(f"Error processing closed POLYLINE: {e}")
                            skipped_count += 1
                    
                    elif entity_dxf_type == 'CIRCLE':
                        # Convert circle to polygon approximation
                        try:
                            center = entity.dxf.center
                            radius = entity.dxf.radius
                            # Create circle as polygon with 32 points
                            import math
                            points = []
                            for i in range(32):
                                angle = 2 * math.pi * i / 32
                                x = center.x + radius * math.cos(angle)
                                y = center.y + radius * math.sin(angle)
                                points.append((x, y))
                            # Close the polygon
                            points.append(points[0])
                            
                            polygon = Polygon(points)
                            geometries.append(polygon)
                            processed_count += 1
                            logging.debug(f"Processed CIRCLE at ({center.x}, {center.y}) with radius {radius}")
                        except Exception as e:
                            logging.warning(f"Error processing CIRCLE: {e}")
                            skipped_count += 1
                    
                    else:
                        skipped_count += 1
                
                else:
                    skipped_count += 1
            
            except Exception as e:
                skipped_count += 1
                logging.warning(f"Error processing entity {entity.dxftype()}: {str(e)}")
        
        logging.info(f"Extraction complete: {processed_count} processed, {skipped_count} skipped")
        logging.info(f"Looking for: {entity_type}")
        logging.info(f"Entity types in DXF: {entity_type_counts}")
        
        return geometries
    
    @staticmethod
    def extract_from_shp_auto_detect(gdf):
        """
        Extract geometries from shapefile GeoDataFrame with automatic type detection
        
        Args:
            gdf: GeoDataFrame from shapefile
        
        Returns:
            tuple: (geometries_list, detected_entity_type)
        """
        geometries = []
        processed_count = 0
        skipped_count = 0
        
        # First, detect the primary geometry type
        geometry_counts = {}
        for geom in gdf.geometry:
            if geom is not None and not geom.is_empty:
                geom_type = geom.geom_type
                geometry_counts[geom_type] = geometry_counts.get(geom_type, 0) + 1
        
        if not geometry_counts:
            return [], "Unknown"
        
        # Find the most common geometry type
        primary_geom_type = max(geometry_counts, key=geometry_counts.get)
        
        # Map to our entity types
        if primary_geom_type in ['Point', 'MultiPoint']:
            detected_entity_type = "Points"
        elif primary_geom_type in ['LineString', 'MultiLineString']:
            detected_entity_type = "Lines"
        elif primary_geom_type in ['Polygon', 'MultiPolygon']:
            detected_entity_type = "Polygons/Areas"
        else:
            detected_entity_type = "Unknown"
        
        logging.info(f"Auto-detected entity type: {detected_entity_type} (primary: {primary_geom_type})")
        
        # Extract geometries based on detected type
        for idx, geom in enumerate(gdf.geometry):
            try:
                if geom is None or geom.is_empty:
                    skipped_count += 1
                    continue
                
                # Handle Points
                if geom.geom_type == 'Point':
                    geometries.append(Point(geom.coords[0]))
                    processed_count += 1
                elif geom.geom_type == 'MultiPoint':
                    # Split multi-point into individual points
                    for point in geom.geoms:
                        geometries.append(Point(point.coords[0]))
                        processed_count += 1
                
                # Handle Lines
                elif geom.geom_type == 'LineString':
                    geometries.append(LineString(geom.coords))
                    processed_count += 1
                elif geom.geom_type == 'MultiLineString':
                    # Split multi-line into individual lines
                    for line in geom.geoms:
                        geometries.append(LineString(line.coords))
                        processed_count += 1
                
                # Handle Polygons
                elif geom.geom_type == 'Polygon':
                    # Only use exterior ring for DXF compatibility
                    geometries.append(Polygon(geom.exterior.coords))
                    processed_count += 1
                elif geom.geom_type == 'MultiPolygon':
                    # Split multi-polygon into individual polygons
                    for poly in geom.geoms:
                        geometries.append(Polygon(poly.exterior.coords))
                        processed_count += 1
                
                else:
                    skipped_count += 1
            
            except Exception as e:
                skipped_count += 1
                logging.warning(f"Error processing geometry at index {idx}: {str(e)}")
        
        logging.info(f"Extraction complete: {processed_count} processed, {skipped_count} skipped")
        return geometries, detected_entity_type

class ConverterEngine:
    """Core conversion logic separated from GUI"""
    
    @staticmethod
    def dxf_to_shp(dxf_path, shp_path, datum, zone, entity_type):
        """
        Convert DXF file to Shapefile
        
        Args:
            dxf_path: Path to input DXF file
            shp_path: Path to output SHP file
            datum: Coordinate datum ('GDA1994' or 'GDA2020')
            zone: MGA zone number
            entity_type: Type of entities to convert
        """
        logging.info(f"Starting DXF to SHP conversion: {dxf_path} -> {shp_path}")
        
        try:
            # Read DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            
            # Extract geometries based on entity type
            geometries = GeometryExtractor.extract_from_dxf(msp, entity_type)
            
            if not geometries:
                raise ValueError(f"No {entity_type} found in the DXF file. "
                               f"Please check the entity type selection or DXF content.")
            
            # Determine CRS (Coordinate Reference System)
            base_epsg = (Config.GDA1994_BASE_EPSG if datum == "GDA1994" 
                        else Config.GDA2020_BASE_EPSG)
            crs = f"EPSG:{base_epsg + int(zone)}"
            
            # Create GeoDataFrame with proper CRS
            gdf = gpd.GeoDataFrame(geometry=geometries, crs=crs)
            
            # Add some basic attributes
            gdf['id'] = range(1, len(gdf) + 1)
            gdf['entity_type'] = entity_type
            gdf['source_file'] = Path(dxf_path).name
            
            # Save to shapefile
            gdf.to_file(shp_path, driver='ESRI Shapefile')
            
            logging.info(f"Successfully converted {len(geometries)} {entity_type} to {shp_path}")
            return len(geometries)
            
        except ezdxf.DXFStructureError as e:
            raise ValueError(f"Invalid DXF file structure: {str(e)}")
        except Exception as e:
            logging.error(f"DXF to SHP conversion failed: {str(e)}")
            raise
    
    @staticmethod
    def shp_to_dxf(shp_path, dxf_path, dxf_version, binary_dxf):
        """
        Convert Shapefile to DXF file with automatic geometry type detection
        
        Args:
            shp_path: Path to input SHP file
            dxf_path: Path to output DXF file
            dxf_version: DXF format version
            binary_dxf: Whether to save as binary DXF
            
        Returns:
            tuple: (converted_count, detected_entity_type)
        """
        logging.info(f"Starting SHP to DXF conversion: {shp_path} -> {dxf_path}")
        
        try:
            # Read shapefile
            gdf = gpd.read_file(shp_path)
            
            if gdf.empty:
                raise ValueError("Shapefile is empty or contains no valid geometries")
            
            # Create new DXF document
            doc = ezdxf.new(dxf_version)
            msp = doc.modelspace()
            
            # Extract geometries with automatic type detection
            geometries, detected_entity_type = GeometryExtractor.extract_from_shp_auto_detect(gdf)
            
            if not geometries:
                raise ValueError("No compatible geometries found in the shapefile.")
            
            logging.info(f"Auto-detected geometry type: {detected_entity_type}")
            
            # Convert geometries to DXF entities
            converted_count = 0
            for geom in geometries:
                try:
                    if geom.geom_type == 'Point':
                        # Add point entity
                        coords = geom.coords[0]
                        msp.add_point((coords[0], coords[1], 0))  # Add Z=0 for 3D compatibility
                        converted_count += 1
                    
                    elif geom.geom_type == 'LineString':
                        # Add polyline entity
                        coords = [(x, y) for x, y in geom.coords]
                        msp.add_lwpolyline(coords)
                        converted_count += 1
                    
                    elif geom.geom_type == 'Polygon':
                        # Add closed polyline entity
                        coords = [(x, y) for x, y in geom.exterior.coords]
                        msp.add_lwpolyline(coords, dxfattribs={'closed': True})
                        converted_count += 1
                
                except Exception as e:
                    logging.warning(f"Failed to convert geometry {geom}: {str(e)}")
            
            if converted_count == 0:
                raise ValueError("No geometries could be converted to DXF format")
            
            # Save DXF file
            if binary_dxf:
                # For binary DXF, use saveas with fmt='bin' parameter
                doc.saveas(dxf_path, fmt='bin')
            else:
                # For ASCII DXF, use default saveas method
                doc.saveas(dxf_path)
            
            logging.info(f"Successfully converted {converted_count} geometries to {dxf_path}")
            return converted_count, detected_entity_type
            
        except Exception as e:
            logging.error(f"SHP to DXF conversion failed: {str(e)}")
            raise

class ConverterApp:
    """Main GUI application class with improved error handling and user experience"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{Config.APP_TITLE} v{Config.APP_VERSION}")
        self.root.geometry("500x650")
        self.root.resizable(True, True)
        
        # Set minimum window size to prevent it from becoming too small
        self.root.minsize(450, 600)
        
        # Initialize variables
        self.last_dir = str(Path.home())  # Start from user's home directory
        self.detected_geometry_type = None  # Store detected geometry type for SHP files
        
        # Set up the GUI
        self.setup_styles()
        self.create_widgets()
        
        # Center window on screen
        self.center_window()
        
        logging.info("Application started")
    
    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure('Convert.TButton', font=('Arial', 10, 'bold'))
        style.configure('Browse.TButton', font=('Arial', 9))
        
        # Configure label styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 9), foreground='gray')
        style.configure('Success.TLabel', font=('Arial', 9), foreground='green')
    
    def center_window(self):
        """Center the application window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create individual tabs
        self.create_shp_to_dxf_tab()
        self.create_dxf_to_shp_tab()
        self.create_about_tab()
    
    def get_system_specs(self):
        """
        Get detailed system specifications including CPU and RAM info.
        Returns a dictionary with system specifications.
        """
        specs = {}
        
        try:
            # First attempt: Try using psutil if available
            import psutil
            
            # CPU Info
            specs['processor'] = platform.processor()
            specs['cpu_cores'] = psutil.cpu_count(logical=True)
            specs['cpu_freq'] = f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "Unknown"
            
            # RAM Info (convert to GB and round to 2 decimal places)
            total_ram = psutil.virtual_memory().total
            specs['ram'] = f"{total_ram / (1024**3):.2f} GB"
            
        except ImportError:
            # Fallback for Windows: Use wmic commands
            if platform.system() == 'Windows':
                try:
                    # Get CPU info
                    cpu = subprocess.check_output('wmic cpu get name, maxclockspeed', shell=True).decode()
                    cpu_lines = cpu.strip().split('\n')[1:]  # Skip header
                    if cpu_lines:
                        specs['processor'] = cpu_lines[0].strip()
                    
                    # Get logical processors count
                    cpu_count = subprocess.check_output('wmic cpu get NumberOfLogicalProcessors', shell=True).decode()
                    count_lines = cpu_count.strip().split('\n')[1:]
                    if count_lines:
                        specs['cpu_cores'] = count_lines[0].strip()
                    
                    # Get RAM info
                    ram = subprocess.check_output('wmic computersystem get totalphysicalmemory', shell=True).decode()
                    ram_lines = ram.strip().split('\n')[1:]
                    if ram_lines:
                        ram_bytes = int(ram_lines[0].strip())
                        specs['ram'] = f"{ram_bytes / (1024**3):.2f} GB"
                        
                except:
                    # If wmic fails, use basic info
                    specs['processor'] = platform.processor()
                    specs['cpu_cores'] = "Unknown"
                    specs['ram'] = "Unknown"
            else:
                # For non-Windows systems, use basic info
                specs['processor'] = platform.processor()
                specs['cpu_cores'] = "Unknown"
                specs['ram'] = "Unknown"
        
        return specs
  
    def create_shp_to_dxf_tab(self):
        """Create the SHP to DXF conversion tab with auto-detection"""
        # Create tab frame
        self.shp_to_dxf_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.shp_to_dxf_tab, text="SHP → DXF")
        
        # Main frame with padding
        main_frame = ttk.Frame(self.shp_to_dxf_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Convert Shapefile to DXF", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Input file selection
        ttk.Label(main_frame, text="Input SHP File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.shp_input_entry = ttk.Entry(main_frame, width=35)
        self.shp_input_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        # Bind the entry change event to detect geometry type
        self.shp_input_entry.bind('<KeyRelease>', self.on_shp_input_change)
        ttk.Button(main_frame, text="Browse...", style='Browse.TButton',
                  command=self.browse_shp_input_file).grid(row=1, column=2, padx=5, pady=5)
        
        # Geometry type detection display
        self.geometry_detection_frame = ttk.LabelFrame(main_frame, text="Detected Shapefile Information", padding=10)
        self.geometry_detection_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Geometry type info
        geometry_info_frame = ttk.Frame(self.geometry_detection_frame)
        geometry_info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        ttk.Label(geometry_info_frame, text="Geometry Type:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, sticky="w")
        self.detected_type_label = ttk.Label(geometry_info_frame, 
                                           text="No shapefile selected", 
                                           style='Info.TLabel')
        self.detected_type_label.grid(row=0, column=1, padx=5, sticky="w")
        
        # CRS info
        crs_info_frame = ttk.Frame(self.geometry_detection_frame)
        crs_info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        ttk.Label(crs_info_frame, text="Coordinate System:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, sticky="w")
        self.detected_crs_label = ttk.Label(crs_info_frame, 
                                          text="Unknown", 
                                          style='Info.TLabel')
        self.detected_crs_label.grid(row=0, column=1, padx=5, sticky="w")
        
        # Detailed CRS info
        details_info_frame = ttk.Frame(self.geometry_detection_frame)
        details_info_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        ttk.Label(details_info_frame, text="Details:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, sticky="w")
        self.detected_details_label = ttk.Label(details_info_frame, 
                                              text="Select a shapefile to see coordinate system details", 
                                              style='Info.TLabel',
                                              wraplength=350)
        self.detected_details_label.grid(row=0, column=1, padx=5, sticky="w")
        
        # Configure column weights
        geometry_info_frame.columnconfigure(1, weight=1)
        crs_info_frame.columnconfigure(1, weight=1)
        details_info_frame.columnconfigure(1, weight=1)
        
        # Output file selection
        ttk.Label(main_frame, text="Output DXF File:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.dxf_output_entry = ttk.Entry(main_frame, width=35)
        self.dxf_output_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Browse...", style='Browse.TButton',
                  command=lambda: self.browse_output_file(self.dxf_output_entry, Config.DXF_FILETYPES)).grid(row=3, column=2, padx=5, pady=5)
        
        # DXF settings
        dxf_settings_frame = ttk.LabelFrame(main_frame, text="DXF Output Settings", padding=10)
        dxf_settings_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")
        
        # DXF version
        ttk.Label(dxf_settings_frame, text="DXF Version:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.dxf_version_var = tk.StringVar(value="R2018")
        version_combo = ttk.Combobox(dxf_settings_frame, textvariable=self.dxf_version_var, 
                                    values=Config.SUPPORTED_DXF_VERSIONS, state="readonly", width=15)
        version_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Binary DXF option
        self.binary_dxf_var = tk.BooleanVar(value=False)
        binary_check = ttk.Checkbutton(dxf_settings_frame, text="Save as Binary DXF (smaller file size)", 
                                      variable=self.binary_dxf_var)
        binary_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Info label - updated to reflect auto-detection
        info_label = ttk.Label(main_frame, text="Geometry type and coordinate system information will be automatically detected", style='Info.TLabel')
        info_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # Convert button and progress bar
        self.shp_convert_button = ttk.Button(main_frame, text="Convert", style='Convert.TButton',
                                           command=self.convert_shp_to_dxf)
        self.shp_convert_button.grid(row=6, column=1, pady=10)
        
        self.shp_progress = ttk.Progressbar(main_frame, length=300, mode="indeterminate")
        self.shp_progress.grid(row=7, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Configure column weights for responsive layout
        main_frame.columnconfigure(1, weight=1)
        dxf_settings_frame.columnconfigure(1, weight=1)

    def create_dxf_to_shp_tab(self):
        """Create the DXF to SHP conversion tab"""
        # Create tab frame
        self.dxf_to_shp_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dxf_to_shp_tab, text="DXF → SHP")
        
        # Main frame with padding
        main_frame = ttk.Frame(self.dxf_to_shp_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Convert DXF to Shapefile", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Input file selection
        ttk.Label(main_frame, text="Input DXF File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.dxf_input_entry = ttk.Entry(main_frame, width=35)
        self.dxf_input_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Browse...", style='Browse.TButton',
                  command=lambda: self.browse_input_file(self.dxf_input_entry, Config.DXF_FILETYPES)).grid(row=1, column=2, padx=5, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output SHP File:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.shp_output_entry = ttk.Entry(main_frame, width=35)
        self.shp_output_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Browse...", style='Browse.TButton',
                  command=lambda: self.browse_output_file(self.shp_output_entry, Config.SHP_FILETYPES)).grid(row=2, column=2, padx=5, pady=5)
        
        # Coordinate system settings
        settings_frame = ttk.LabelFrame(main_frame, text="Coordinate System Settings", padding=10)
        settings_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Datum selection
        ttk.Label(settings_frame, text="Datum:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.datum_var = tk.StringVar(value="GDA2020")  # Default to newer datum
        datum_combo = ttk.Combobox(settings_frame, textvariable=self.datum_var, 
                                  values=["GDA1994", "GDA2020"], state="readonly", width=15)
        datum_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Zone selection
        ttk.Label(settings_frame, text="MGA Zone:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.zone_var = tk.StringVar(value="55")  # Default to zone 55 (common for Melbourne/Sydney)
        zone_combo = ttk.Combobox(settings_frame, textvariable=self.zone_var, 
                                 values=Config.SUPPORTED_ZONES, state="readonly", width=10)
        zone_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Entity type selection (still needed for DXF since it can contain mixed types)
        ttk.Label(main_frame, text="Entity Type:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entity_type_var = tk.StringVar(value="Points")
        entity_combo = ttk.Combobox(main_frame, textvariable=self.entity_type_var, 
                                   values=Config.SUPPORTED_ENTITY_TYPES, state="readonly", width=20)
        entity_combo.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Info label
        info_label = ttk.Label(main_frame, text="Select the type of DXF entities to convert", style='Info.TLabel')
        info_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # Convert button and progress bar
        self.dxf_convert_button = ttk.Button(main_frame, text="Convert", style='Convert.TButton',
                                           command=self.convert_dxf_to_shp)
        self.dxf_convert_button.grid(row=6, column=1, pady=10)
        
        self.dxf_progress = ttk.Progressbar(main_frame, length=300, mode="indeterminate")
        self.dxf_progress.grid(row=7, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Configure column weights for responsive layout
        main_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)

    def create_about_tab(self):
        """Create the about/help tab with scrollable text"""
        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text="About & Help")
        
        # Main frame with padding
        main_frame = ttk.Frame(self.about_tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a frame for the text widget and scrollbars
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        # Create scrollable text widget with console font and NO text wrapping
        self.about_text = tk.Text(text_frame, 
                                 wrap=tk.NONE,  # No text wrapping - enables horizontal scrolling
                                 font=('Consolas', 10),  # Console font
                                 bg='white',
                                 fg='black',
                                 padx=15,
                                 pady=15,
                                 state=tk.DISABLED,  # Make it read-only
                                 cursor='arrow')  # Change cursor to indicate read-only
        
        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.about_text.yview)
        self.about_text.configure(yscrollcommand=v_scrollbar.set)
        
        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=self.about_text.xview)
        self.about_text.configure(xscrollcommand=h_scrollbar.set)
        
        # Grid layout for text widget and scrollbars
        self.about_text.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights so text widget expands
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       
        # Get system specifications
        specs = self.get_system_specs()
        
        # Application info content
        app_info = f"""{Config.APP_TITLE}
Version {Config.APP_VERSION}

A tool for converting between DXF and Shapefile formats
with support for Australian coordinate systems.

================================================================================
SUPPORTED FEATURES:
================================================================================
• Convert DXF to Shapefile with MGA coordinate systems
• Convert Shapefile to DXF with automatic geometry detection
• Support for Points, Lines, and Polygons/Areas
• GDA1994 and GDA2020 datum support
• MGA Zones 50-56 (Australia)
• Binary and ASCII DXF output formats
• Real-time coordinate reference system detection

================================================================================
SUPPORTED ENTITY TYPES:
================================================================================
• Points (DXF POINT entities, SHP Point/MultiPoint)
• Lines (DXF LINE and open LWPOLYLINE, SHP LineString/MultiLineString)
• Polygons/Areas (closed LWPOLYLINE and CIRCLE, SHP Polygon/MultiPolygon)

================================================================================
COORDINATE SYSTEMS:
================================================================================
• GDA1994 MGA: EPSG:283xx (where xx is the zone number)
  - Zone 50: EPSG:28350    - Zone 53: EPSG:28353    - Zone 56: EPSG:28356
  - Zone 51: EPSG:28351    - Zone 54: EPSG:28354
  - Zone 52: EPSG:28352    - Zone 55: EPSG:28355

• GDA2020 MGA: EPSG:785x (where x is the zone number)
  - Zone 50: EPSG:7850     - Zone 53: EPSG:7853     - Zone 56: EPSG:7856
  - Zone 51: EPSG:7851     - Zone 54: EPSG:7854
  - Zone 52: EPSG:7852     - Zone 55: EPSG:7855

• Geographic Coordinate Systems:
  - GDA1994: EPSG:4283
  - GDA2020: EPSG:7844

================================================================================
AUSTRALIAN MGA ZONE COVERAGE:
================================================================================
Zone 50: Western Australia (west)    Zone 54: Northern Territory, Queensland
Zone 51: Western Australia (east)    Zone 55: New South Wales, Victoria, Tasmania
Zone 52: South Australia (west)      Zone 56: New South Wales, Queensland (east)
Zone 53: South Australia (east)

================================================================================
NEW IN VERSION 2.1:
================================================================================
• Automatic geometry type detection for SHP → DXF conversion
• Coordinate Reference System (CRS) detection and display
• Australian datum support (GDA1994, GDA2020) with MGA zone detection
• Real-time shapefile analysis with CRS information
• Enhanced user interface with detailed coordinate system feedback
• Improved error handling and validation

================================================================================
IMPORTANT NOTES:
================================================================================
• DXF files do not contain coordinate reference system information
• Always document the coordinate system used when sharing DXF files
• Consider naming DXF files with CRS info (e.g., survey_GDA2020_MGA55.dxf)
• Non-Australian coordinate systems will trigger warnings
• Shapefiles without CRS definitions may cause coordinate interpretation issues

================================================================================
TECHNICAL INFORMATION:
================================================================================
Dependencies:
• tkinter (GUI framework)
• geopandas (spatial data handling)
• ezdxf (DXF file processing)
• shapely (geometry operations)

Log files are created in the application directory with naming pattern:
converter_YYYYMMDD.log

For technical support or feature requests, please check the application
log file for detailed information about conversion processes and any errors.

================================================================================
LICENSE AND COPYRIGHT:
================================================================================

Version: {__version__}
{__copyright__}
{__license__}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

System Information:
------------------
OS: {platform.system()} {platform.version()}
Architecture: {platform.machine()}
Python Version: {sys.version.split()[0]}
Running on: {platform.node()}
Started on: {current_time}

Hardware Information:
------------------
Processor: {specs.get('processor', 'Unknown')}
Logical Processors: {specs.get('cpu_cores', 'Unknown')}
Processor Speed: {specs.get('cpu_freq', 'Unknown')}
Total RAM: {specs.get('ram', 'Unknown')}
"""
        
        # Insert the text into the widget
        self.about_text.config(state=tk.NORMAL)  # Enable editing temporarily
        self.about_text.insert(tk.END, app_info)
        self.about_text.config(state=tk.DISABLED)  # Make it read-only again
    
    def on_shp_input_change(self, event=None):
        """Handle changes to the SHP input field to detect geometry type and CRS"""
        # Reset detection display when user types
        self.detected_type_label.config(text="Type to detect...", style='Info.TLabel')
        self.detected_crs_label.config(text="Analyzing...", style='Info.TLabel')
        self.detected_details_label.config(text="Analyzing coordinate system...", style='Info.TLabel')
        self.detected_geometry_type = None
        
        # Schedule detection after a short delay to avoid constant checking while typing
        if hasattr(self, '_detection_timer'):
            self.root.after_cancel(self._detection_timer)
        
        self._detection_timer = self.root.after(500, self.detect_shapefile_info_delayed)
    
    def detect_shapefile_info_delayed(self):
        """Detect shapefile information after a delay"""
        shp_path = self.shp_input_entry.get().strip()
        if shp_path and Path(shp_path).exists() and shp_path.lower().endswith('.shp'):
            self.detect_and_display_shapefile_info(shp_path)
    
    def browse_shp_input_file(self):
        """Browse and select SHP input file with automatic information detection"""
        filepath = filedialog.askopenfilename(
            title="Select Shapefile",
            filetypes=Config.SHP_FILETYPES,
            initialdir=self.last_dir
        )
        
        if filepath:
            # Validate the selected file
            is_valid, message = FileValidator.validate_file_exists(filepath)
            
            if is_valid:
                self.shp_input_entry.delete(0, tk.END)
                self.shp_input_entry.insert(0, filepath)
                self.last_dir = str(Path(filepath).parent)
                logging.info(f"Selected SHP input file: {filepath}")
                
                # Immediately detect shapefile information
                self.detect_and_display_shapefile_info(filepath)
            else:
                messagebox.showerror("File Error", f"Invalid file selection:\n{message}")
    
    def detect_and_display_shapefile_info(self, shp_path):
        """Detect and display both geometry type and CRS information of the selected shapefile"""
        try:
            # Show detection in progress
            self.detected_type_label.config(text="Detecting...", style='Info.TLabel')
            self.detected_crs_label.config(text="Analyzing...", style='Info.TLabel')
            self.detected_details_label.config(text="Reading coordinate system information...", style='Info.TLabel')
            self.root.update_idletasks()
            
            # Detect shapefile information (geometry + CRS)
            info = GeometryDetector.detect_shapefile_info(shp_path)
            
            if info['error']:
                # Error - display error message
                self.detected_geometry_type = None
                self.detected_type_label.config(text=f"✗ Error: {info['error']}", style='Info.TLabel')
                self.detected_crs_label.config(text="Unknown", style='Info.TLabel')
                self.detected_details_label.config(text="Could not analyze coordinate system", style='Info.TLabel')
                logging.warning(f"Failed to detect shapefile info: {info['error']}")
                return
            
            # Display geometry type information
            self.detected_geometry_type = info['readable_name']
            geom_display_text = f"✓ {info['readable_name']} ({info['feature_count']} features)"
            self.detected_type_label.config(text=geom_display_text, style='Success.TLabel')
            
            # Display CRS information
            crs_info = info['crs_info']
            if crs_info is None:
                self.detected_crs_label.config(text="✗ No CRS defined", style='Info.TLabel')
                self.detected_details_label.config(
                    text="Warning: Shapefile has no coordinate reference system defined. "
                         "This may cause issues with coordinate interpretation.", 
                    style='Info.TLabel'
                )
            elif crs_info['is_australian']:
                # Australian CRS detected
                if crs_info['projection'] == 'MGA':
                    crs_display = f"✓ {crs_info['datum']} MGA Zone {crs_info['zone']}"
                    details_text = (f"Datum: {crs_info['datum']} | "
                                  f"Projection: {crs_info['projection']} | "
                                  f"Zone: {crs_info['zone']}")
                    if crs_info['epsg_code']:
                        details_text += f" | EPSG: {crs_info['epsg_code']}"
                    
                    self.detected_crs_label.config(text=crs_display, style='Success.TLabel')
                    self.detected_details_label.config(text=details_text, style='Success.TLabel')
                    
                    logging.info(f"Australian MGA CRS detected: {crs_info['datum']} Zone {crs_info['zone']}")
                    
                else:
                    # Australian but not MGA
                    crs_display = f"✓ {crs_info['datum']} ({crs_info['projection']})"
                    details_text = (f"Datum: {crs_info['datum']} | "
                                  f"Projection: {crs_info['projection']}")
                    if crs_info['epsg_code']:
                        details_text += f" | EPSG: {crs_info['epsg_code']}"
                    
                    self.detected_crs_label.config(text=crs_display, style='Success.TLabel')
                    self.detected_details_label.config(text=details_text, style='Info.TLabel')
            else:
                # Non-Australian CRS
                if crs_info['epsg_code']:
                    crs_display = f"⚠ Non-Australian (EPSG:{crs_info['epsg_code']})"
                    details_text = (f"Warning: Non-Australian coordinate system detected. "
                                  f"EPSG: {crs_info['epsg_code']}. Consider reprojecting to Australian datum.")
                else:
                    crs_display = "⚠ Non-Australian CRS"
                    details_text = (f"Warning: Non-Australian coordinate system detected. "
                                  f"Consider reprojecting to GDA1994 or GDA2020 MGA.")
                
                self.detected_crs_label.config(text=crs_display, style='Info.TLabel')
                self.detected_details_label.config(text=details_text, style='Info.TLabel')
                
                logging.warning(f"Non-Australian CRS detected: {crs_info}")
            
            logging.info(f"Shapefile analysis complete: {info['readable_name']}, CRS: {crs_info}")
        
        except Exception as e:
            # Handle unexpected errors
            self.detected_geometry_type = None
            error_msg = f"✗ Analysis failed: {str(e)}"
            self.detected_type_label.config(text=error_msg, style='Info.TLabel')
            self.detected_crs_label.config(text="Unknown", style='Info.TLabel')
            self.detected_details_label.config(text="Could not analyze shapefile", style='Info.TLabel')
            logging.error(f"Shapefile analysis error: {str(e)}")
    
    def detect_and_display_geometry_type(self, shp_path):
        """Legacy method - now redirects to full shapefile info detection"""
        self.detect_and_display_shapefile_info(shp_path)
    
    def browse_input_file(self, entry_widget, filetypes):
        """Browse and select input file with validation"""
        filepath = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=filetypes,
            initialdir=self.last_dir
        )
        
        if filepath:
            # Validate the selected file
            is_valid, message = FileValidator.validate_file_exists(filepath)
            
            if is_valid:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, filepath)
                self.last_dir = str(Path(filepath).parent)
                logging.info(f"Selected input file: {filepath}")
            else:
                messagebox.showerror("File Error", f"Invalid file selection:\n{message}")
    
    def browse_output_file(self, entry_widget, filetypes):
        """Browse and select output file location with validation"""
        filepath = filedialog.asksaveasfilename(
            title="Select Output File Location",
            filetypes=filetypes,
            defaultextension=filetypes[0][1].replace("*", ""),
            initialdir=self.last_dir
        )
        
        if filepath:
            # Validate the output path
            is_valid, message = FileValidator.validate_output_path(filepath)
            
            if is_valid:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, filepath)
                self.last_dir = str(Path(filepath).parent)
                logging.info(f"Selected output file: {filepath}")
            else:
                messagebox.showerror("Path Error", f"Invalid output path:\n{message}")
    
    def validate_conversion_inputs(self, input_path, output_path, input_ext, output_ext):
        """
        Validate inputs before starting conversion
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if paths are provided
        if not input_path.strip():
            return False, "Please select an input file"
        
        if not output_path.strip():
            return False, "Please select an output file location"
        
        # Validate input file
        is_valid, message = FileValidator.validate_file_exists(input_path)
        if not is_valid:
            return False, f"Input file error: {message}"
        
        # Validate file extensions
        is_valid, message = FileValidator.validate_file_extension(input_path, input_ext)
        if not is_valid:
            return False, f"Input file error: {message}"
        
        is_valid, message = FileValidator.validate_file_extension(output_path, output_ext)
        if not is_valid:
            return False, f"Output file error: {message}"
        
        # Validate output path
        is_valid, message = FileValidator.validate_output_path(output_path)
        if not is_valid:
            return False, f"Output path error: {message}"
        
        # Check if output file exists and confirm overwrite
        if Path(output_path).exists():
            response = messagebox.askyesno(
                "File Exists", 
                f"The output file already exists:\n{output_path}\n\nDo you want to overwrite it?"
            )
            if not response:
                return False, "Conversion cancelled by user"
        
        return True, "Validation successful"
    
    def convert_dxf_to_shp(self):
        """Handle DXF to SHP conversion with comprehensive error handling"""
        # Get input values
        dxf_path = self.dxf_input_entry.get().strip()
        shp_path = self.shp_output_entry.get().strip()
        datum = self.datum_var.get()
        zone = self.zone_var.get()
        entity_type = self.entity_type_var.get()
        
        # Validate inputs
        is_valid, error_message = self.validate_conversion_inputs(
            dxf_path, shp_path, '.dxf', '.shp'
        )
        
        if not is_valid:
            messagebox.showwarning("Validation Error", error_message)
            return
        
        # Disable UI during conversion
        self.set_conversion_ui_state(False, "dxf_to_shp")
        
        def run_conversion():
            """Run the actual conversion in a separate thread"""
            try:
                logging.info(f"Starting DXF to SHP conversion")
                logging.info(f"Input: {dxf_path}")
                logging.info(f"Output: {shp_path}")
                logging.info(f"Settings: {datum}, Zone {zone}, {entity_type}")
                
                # Perform the conversion
                converted_count = ConverterEngine.dxf_to_shp(
                    dxf_path, shp_path, datum, zone, entity_type
                )
                
                # Show success message
                success_msg = (f"Conversion completed successfully!\n\n"
                              f"Converted {converted_count} {entity_type.lower()} from DXF to Shapefile.\n"
                              f"Output saved to: {shp_path}")
                
                self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
                logging.info(f"DXF to SHP conversion completed successfully")
                
            except Exception as e:
                error_msg = f"Conversion failed:\n\n{str(e)}"
                logging.error(f"DXF to SHP conversion failed: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Conversion Error", error_msg))
            
            finally:
                # Re-enable UI
                self.root.after(0, lambda: self.set_conversion_ui_state(True, "dxf_to_shp"))
        
        # Start conversion in separate thread to prevent UI freezing
        thread = threading.Thread(target=run_conversion, daemon=True)
        thread.start()
    
    def convert_shp_to_dxf(self):
        """Handle SHP to DXF conversion with automatic geometry detection"""
        # Get input values
        shp_path = self.shp_input_entry.get().strip()
        dxf_path = self.dxf_output_entry.get().strip()
        dxf_version = self.dxf_version_var.get()
        binary_dxf = self.binary_dxf_var.get()
        
        # Validate inputs
        is_valid, error_message = self.validate_conversion_inputs(
            shp_path, dxf_path, '.shp', '.dxf'
        )
        
        if not is_valid:
            messagebox.showwarning("Validation Error", error_message)
            return
        
        # Check if geometry type was detected
        if not self.detected_geometry_type:
            # Try to detect it now if not already done
            self.detect_and_display_shapefile_info(shp_path)
            
            if not self.detected_geometry_type:
                messagebox.showwarning("Shapefile Analysis Error", 
                                     "Could not analyze the shapefile. "
                                     "Please ensure the file is a valid shapefile with supported geometry types.")
                return
        
        # Disable UI during conversion
        self.set_conversion_ui_state(False, "shp_to_dxf")
        
        def run_conversion():
            """Run the actual conversion in a separate thread"""
            try:
                logging.info(f"Starting SHP to DXF conversion")
                logging.info(f"Input: {shp_path}")
                logging.info(f"Output: {dxf_path}")
                logging.info(f"Settings: {dxf_version}, Binary: {binary_dxf}")
                logging.info(f"Detected geometry type: {self.detected_geometry_type}")
                
                # Perform the conversion with auto-detection
                converted_count, detected_entity_type = ConverterEngine.shp_to_dxf(
                    shp_path, dxf_path, dxf_version, binary_dxf
                )
                
                # Show success message
                file_type = "Binary DXF" if binary_dxf else "ASCII DXF"
                success_msg = (f"Conversion completed successfully!\n\n"
                              f"Detected and converted {converted_count} {detected_entity_type.lower()} "
                              f"from Shapefile to {file_type}.\n"
                              f"Output saved to: {dxf_path}")
                
                self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
                logging.info(f"SHP to DXF conversion completed successfully")
                
            except Exception as e:
                error_msg = f"Conversion failed:\n\n{str(e)}"
                logging.error(f"SHP to DXF conversion failed: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Conversion Error", error_msg))
            
            finally:
                # Re-enable UI
                self.root.after(0, lambda: self.set_conversion_ui_state(True, "shp_to_dxf"))
        
        # Start conversion in separate thread to prevent UI freezing
        thread = threading.Thread(target=run_conversion, daemon=True)
        thread.start()
    
    def set_conversion_ui_state(self, enabled, conversion_type):
        """
        Enable or disable UI elements during conversion
        
        Args:
            enabled: True to enable UI, False to disable
            conversion_type: 'dxf_to_shp' or 'shp_to_dxf'
        """
        state = "normal" if enabled else "disabled"
        
        if conversion_type == "dxf_to_shp":
            self.dxf_convert_button.config(state=state)
            if enabled:
                self.dxf_convert_button.config(text="Convert")
                self.dxf_progress.stop()
            else:
                self.dxf_convert_button.config(text="Converting...")
                self.dxf_progress.start(10)  # Start progress animation
        
        elif conversion_type == "shp_to_dxf":
            self.shp_convert_button.config(state=state)
            if enabled:
                self.shp_convert_button.config(text="Convert")
                self.shp_progress.stop()
            else:
                self.shp_convert_button.config(text="Converting...")
                self.shp_progress.start(10)  # Start progress animation

def main():
    """Main application entry point with error handling"""
    try:
        # Create and configure the main window
        root = tk.Tk()
        
        # Set window icon if available (optional)
        try:
            # You can add an icon file here if you have one
            # root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # Create the application
        app = ConverterApp(root)
        
        # Handle window closing
        def on_closing():
            """Handle application closing"""
            logging.info("Application closing")
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        # Handle any critical errors during startup
        logging.critical(f"Critical error during application startup: {str(e)}")
        try:
            messagebox.showerror(
                "Critical Error", 
                f"Failed to start the application:\n\n{str(e)}\n\n"
                f"Please check the log file for more details."
            )
        except:
            print(f"Critical error: {str(e)}")

# Run the application when script is executed directly
if __name__ == "__main__":
    main()