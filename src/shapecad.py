# -*- coding: utf-8 -*-

__version__ = "1.0.0"
__author__ = "Daniel Adi Nugroho"
__email__ = "dnugroho@gmail.com"
__status__ = "Production"
__date__ = "2023-10-25"
__copyright__ = "Copyright (c) 2023 Daniel Adi Nugroho"
__license__ = "GNU General Public License v3.0 (GPL-3.0)"

# Version History
# --------------

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
Geospatial File Converter
========================

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

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ezdxf
from shapely.geometry import shape, Point, LineString, Polygon
import shapefile
print("All libraries imported successfully.")  # Debug message

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Converter")
        self.root.geometry("500x300")  # Fixed size for the form window

        self.conversion_type = None
        self.source_file = None
        self.target_file = None
        self.dxf_version = "R2018"
        self.coord_system = "MGA2020"
        self.mga_zone = 50
        self.feature_type = "Polygon"  # Default feature type

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Conversion Type")
        self.notebook.add(self.tab2, text="File Selection")
        self.notebook.add(self.tab3, text="Options")

        self.create_tab1()
        self.create_tab2()
        self.update_tab3()

        # Disable the third tab initially
        self.notebook.tab(2, state="disabled")

    def create_tab1(self):
        tk.Label(self.tab1, text="Select Conversion Type").pack(pady=10)
        self.conversion_type = tk.StringVar(value="SHP to DXF")
        tk.Radiobutton(self.tab1, text="SHP to DXF", variable=self.conversion_type, value="SHP to DXF", command=self.update_tab3).pack()
        tk.Radiobutton(self.tab1, text="DXF to SHP", variable=self.conversion_type, value="DXF to SHP", command=self.update_tab3).pack()

        # Next button for the first tab (centered at the bottom)
        button_frame = tk.Frame(self.tab1)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        next_button = tk.Button(button_frame, text="Next", command=self.next_tab)
        next_button.pack()

    def create_tab2(self):
        tk.Label(self.tab2, text="Select Source and Target Files").pack(pady=10)
        tk.Button(self.tab2, text="Browse Source File", command=self.browse_source).pack(pady=5)
        self.source_label = tk.Label(self.tab2, text="Source: Not selected")
        self.source_label.pack()
        tk.Button(self.tab2, text="Browse Target File", command=self.browse_target).pack(pady=5)
        self.target_label = tk.Label(self.tab2, text="Target: Not selected")
        self.target_label.pack()

        # Back and Next buttons for the second tab
        button_frame = tk.Frame(self.tab2)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        back_button = tk.Button(button_frame, text="Back", command=self.prev_tab)
        back_button.pack(side=tk.LEFT, padx=10)

        next_button = tk.Button(button_frame, text="Next", command=self.tab2next_button_clicked)
        next_button.pack(side=tk.RIGHT, padx=10)

    def update_tab3(self):
        for widget in self.tab3.winfo_children():
            widget.destroy()

        if self.conversion_type.get() == "SHP to DXF":
            tk.Label(self.tab3, text="DXF Version").pack(pady=10)
            self.dxf_version = tk.StringVar(value="R2018")
            dxf_version_dropdown = ttk.Combobox(self.tab3, textvariable=self.dxf_version, values=["R2010", "R2013", "R2018"], state="readonly")
            dxf_version_dropdown.pack()
        else:
            tk.Label(self.tab3, text="Coordinate System and MGA Zone").pack(pady=10)
            self.coord_system = tk.StringVar(value="MGA2020")
            coord_system_dropdown = ttk.Combobox(self.tab3, textvariable=self.coord_system, values=["MGA1994", "MGA2020"], state="readonly")
            coord_system_dropdown.pack()

            tk.Label(self.tab3, text="MGA Zone").pack()
            self.mga_zone = tk.StringVar(value="50")
            mga_zone_dropdown = ttk.Combobox(self.tab3, textvariable=self.mga_zone, values=[str(i) for i in range(50, 57)], state="readonly")
            mga_zone_dropdown.pack()

            # Feature type dropdown
            tk.Label(self.tab3, text="Feature Type").pack()
            self.feature_type = tk.StringVar(value="Polygon")
            feature_type_dropdown = ttk.Combobox(self.tab3, textvariable=self.feature_type, values=["Point", "Line", "Polygon"], state="readonly")
            feature_type_dropdown.pack()

            # Attempt to read coordinate system and MGA zone from DXF file
            print(self.source_file)  # Debug message
            if self.source_file and self.source_file.endswith(".dxf"):
                print("Reading projection information from DXF file...")  # Debug message
                self.read_dxf_projection_info()

        # Back and Convert buttons for the third tab
        button_frame = tk.Frame(self.tab3)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        back_button = tk.Button(button_frame, text="Back", command=self.prev_tab)
        back_button.pack(side=tk.LEFT, padx=10)

        convert_button = tk.Button(button_frame, text="Convert!", command=self.convert)
        convert_button.pack(side=tk.RIGHT, padx=10)

    def browse_source(self):
        file_types = [("SHP Files", "*.shp")] if self.conversion_type.get() == "SHP to DXF" else [("DXF Files", "*.dxf")]
        self.source_file = filedialog.askopenfilename(filetypes=file_types)
        if self.source_file:
            self.source_label.config(text=f"Source: {self.source_file}")
            self.check_files_selected()

    def browse_target(self):
        file_types = [("DXF Files", "*.dxf")] if self.conversion_type.get() == "SHP to DXF" else [("SHP Files", "*.shp")]
        self.target_file = filedialog.asksaveasfilename(filetypes=file_types, defaultextension=file_types[0][1])
        if self.target_file:
            self.target_label.config(text=f"Target: {self.target_file}")
            self.check_files_selected()

    def check_files_selected(self):
        if self.source_file and self.target_file:
            self.notebook.tab(2, state="normal")
        else:
            self.notebook.tab(2, state="disabled")

    def tab2next_button_clicked(self):
        self.update_tab3() # Update the third tab based on the selected conversion type
        self.next_tab()

    def read_dxf_projection_info(self):
        try:
            print("Attempting to read projection information from DXF file...")  # Debug message
            doc = ezdxf.readfile(self.source_file)
            print("DXF file read successfully.")  # Debug message

            if "ACAD" in doc.header:
                header = doc.header
                projection_found = False

                # Check for coordinate system (PROJCS)
                if "$PROJCS" in header:
                    projcs = header["$PROJCS"]
                    print(f"Found PROJCS: {projcs}")  # Debug message
                    if "MGA1994" in projcs:
                        self.coord_system.set("MGA1994")
                        projection_found = True
                        print("Set coordinate system to MGA1994.")  # Debug message
                    elif "MGA2020" in projcs:
                        self.coord_system.set("MGA2020")
                        projection_found = True
                        print("Set coordinate system to MGA2020.")  # Debug message

                # Check for MGA zone (PROJZONE)
                if "$PROJZONE" in header:
                    self.mga_zone.set(header["$PROJZONE"])
                    projection_found = True
                    print(f"Set MGA zone to {header['$PROJZONE']}.")  # Debug message

                # Notify the user if no projection information is found
                if not projection_found:
                    print("No projection information found in the DXF file.")  # Debug message
                    messagebox.showinfo(
                        "Projection Info",
                        "No projection information found in the DXF file. Please select the coordinate system and MGA zone manually.",
                    )
            else:
                print("No ACAD header found in the DXF file.")  # Debug message
                messagebox.showinfo(
                    "Projection Info",
                    "No projection information found in the DXF file. Please select the coordinate system and MGA zone manually.",
                )
        except Exception as e:
            print(f"Error reading DXF file: {e}")  # Debug message
            messagebox.showinfo(
                "Projection Info",
                f"No projection information found in the DXF file. Please select the coordinate system and MGA zone manually. Error: {e}",
            )

    def next_tab(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab < 2:
            self.notebook.select(current_tab + 1)

    def prev_tab(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab > 0:
            self.notebook.select(current_tab - 1)

    def convert(self):
        if not self.source_file or not self.target_file:
            messagebox.showerror("Error", "Please select source and target files.")
            return

        if self.conversion_type.get() == "SHP to DXF":
            self.convert_shp_to_dxf()
        else:
            self.convert_dxf_to_shp()

        messagebox.showinfo("Success", "Conversion completed successfully!")

    def convert_shp_to_dxf(self):
        print("Converting SHP to DXF...")  # Debug message
        sf = shapefile.Reader(self.source_file)
        doc = ezdxf.new(self.dxf_version.get())
        msp = doc.modelspace()

        for shape_record in sf.shapeRecords():
            geom = shape(shape_record.shape.__geo_interface__)
            if geom.geom_type == "Polygon":
                # Check if the geometry has Z values
                if hasattr(geom, 'z'):
                    points = list(zip(geom.exterior.coords.xy[0], geom.exterior.coords.xy[1], geom.exterior.coords.xy[2]))
                else:
                    points = list(zip(geom.exterior.coords.xy[0], geom.exterior.coords.xy[1], [0] * len(geom.exterior.coords.xy[0])))  # Default Z = 0
                msp.add_lwpolyline(points)
            elif geom.geom_type == "LineString":
                # Check if the geometry has Z values
                if hasattr(geom, 'z'):
                    points = list(zip(geom.coords.xy[0], geom.coords.xy[1], geom.coords.xy[2]))
                else:
                    points = list(zip(geom.coords.xy[0], geom.coords.xy[1], [0] * len(geom.coords.xy[0])))  # Default Z = 0
                msp.add_lwpolyline(points)

        # Save the DXF file
        doc.saveas(self.target_file)

    def convert_dxf_to_shp(self):
        print("Converting DXF to SHP...")
        doc = ezdxf.readfile(self.source_file)
        msp = doc.modelspace()
        w = shapefile.Writer(self.target_file)

        # Add a field for ID
        w.field("ID", "N")

        # Convert based on the selected feature type
        feature_type = self.feature_type.get()
        for entity in msp:
            if feature_type == "Point" and entity.dxftype() == "POINT":
                point = entity.dxf.location
                if hasattr(point, 'z'):  # Check if Z value exists
                    w.point(point.x, point.y, point.z)  # Include Z value
                else:
                    w.point(point.x, point.y)  # Default Z = 0
                w.record(1)
            elif feature_type == "Line" and entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                if entity.dxftype() == "LWPOLYLINE":
                    points = [tuple(point) for point in entity.get_points("xy")]  # Extract XY
                    if hasattr(entity, 'elevation'):  # Check if Z value exists
                        z = entity.dxf.elevation
                        points = [(x, y, z) for (x, y) in points]  # Add Z value
                elif entity.dxftype() == "POLYLINE":
                    points = [(vertex.dxf.location.x, vertex.dxf.location.y, vertex.dxf.location.z) for vertex in entity.vertices]  # Extract XYZ
                w.line([points])
                w.record(1)
            elif feature_type == "Polygon" and entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                if entity.dxftype() == "LWPOLYLINE":
                    points = [tuple(point) for point in entity.get_points("xy")]  # Extract XY
                    if hasattr(entity, 'elevation'):  # Check if Z value exists
                        z = entity.dxf.elevation
                        points = [(x, y, z) for (x, y) in points]  # Add Z value
                elif entity.dxftype() == "POLYLINE":
                    points = [(vertex.dxf.location.x, vertex.dxf.location.y, vertex.dxf.location.z) for vertex in entity.vertices]  # Extract XYZ
                w.poly([points])
                w.record(1)

        w.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()