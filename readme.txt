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