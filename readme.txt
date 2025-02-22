Shapefile-CAD File Converter
============================

This script provides functionality for converting geospatial data between SHP (Shapefile) and DXF (AutoCAD Drawing Exchange Format) formats. 
It supports both 2D and 3D data, preserving elevation information where applicable. The application features a wizard-style GUI built with Tkinter, 
making it user-friendly and intuitive.

Purpose:
--------
- Convert SHP files to DXF format and vice versa
- Preserve elevation (Z values) in 3D data
- Provide a user-friendly GUI for file selection and conversion options
- Support multiple DXF versions (R2010, R2013, R2018)
- Allow selection of coordinate systems (MGA1994, MGA2020) and MGA zones (50 to 56)
- Enable feature type selection (Point, Line, Polygon) for DXF to SHP conversion

Requirements:
------------
- Python 3.8 or higher
- Required packages:
  - tkinter: for the GUI
  - ezdxf: for DXF file handling
  - pyshp (shapefile): for SHP file handling
  - shapely: for geometry operations

Input Formats:
-------------
1. SHP Files:
   - Must contain valid geometry (points, lines, polygons)
   - Supports 2D and 3D data
   - Preserves attribute data (if applicable)

2. DXF Files:
   - Supports entities such as points, lines, polylines, and polygons
   - Preserves layers and other CAD properties
   - Supports 2D and 3D data

Usage:
------
Run the script to launch the GUI:
python shapecad.py

The GUI will guide you through the following steps:
1. Select the conversion type (SHP to DXF or DXF to SHP)
2. Choose the source and target files
3. Set conversion options (DXF version, coordinate system, MGA zone, feature type)
4. Execute the conversion

Output:
-------
- Converted file in the selected format (SHP or DXF)
- Preserves geometry, elevation, and attribute data (if applicable)

Notes:
------
- The application is designed for geospatial data conversion and may not handle non-spatial CAD elements.
- Ensure the input files are valid and contain supported geometry types.
- For large files, the conversion process may take some time.

Acknowledgements:
----------------
- This script was written with the help of DeepSeek R1.
