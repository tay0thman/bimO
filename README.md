# Quickly

A productivity-focused [pyRevit](https://github.com/pyrevitlabs/pyRevit) extension by an architect, for architects.

Quickly is a curated set of Revit tools that streamline the repetitive parts of producing a drawing set — measuring, annotating, coordinating, naming, numbering, and chasing down the small stuff that eats hours every week. Built around the idea that working *smarter* beats working *harder*.

## Status

Beta. Currently being polished panel-by-panel for distribution.

## Supported Revit Versions

Revit **2024 – 2027**. Older versions are out of scope.

## Install

1. Install [pyRevit](https://pyrevitlabs.notion.site/pyRevit-bd907d6292ed4ce997c46e84b6ef67a0) (latest stable).
2. Clone or download this repository.
3. In Revit, open the pyRevit ribbon → **Extensions** → **Settings** and add the repository folder to *Custom Extension Directories*.
4. Reload pyRevit.

The new ribbon tab is named **Quickly**.

## What's in the box

### Quick Measure
Modeless, live-updating WPF windows for fast measurement of selected elements:
- **Quick Area** — sum areas across rooms, walls, floors, sheets, etc., with unit and precision controls
- **Quick Length** — sum lengths (with fractional-inch formatting) of walls, lines, curves
- **Quick Volume** — sum volumes with unit conversions

### Analysis & Dimensioning
- **Find Project Coordinates** — project base point, survey point, true-north angle
- **Find Link's Coordinates** — report coordinates and orientation for selected Revit links
- **Get Area** — quick area sum of selected elements
- **Get Length** — quick length sum of selected walls and curves
- **Find Dim Overrides** — list dimensions with overridden values
- **Find Rounded Dims** — find dimensions whose displayed value differs from the true measurement, with tolerance

### Annotate
- **Flip Grids** — toggle grid bubbles on selected grids
- *(Linetype Manager — under construction; see roadmap)*

### Coordination
- **Select Attached Walls by Type** — find walls attached at top for chosen wall types and levels

### Drawing Set
- **Detail Naming** — bulk-rename viewports to *SheetNumber – DetailNumber – ViewName*
- **Detail Numbering** — auto-number viewports on a sheet based on their position
- **Duplicate Elevations** — duplicate selected elevations with prefix + view template
- **Package Contents** — generate a CSV index of PDFs in a folder
- **Create Revision Print Set** — turn a revision into a printable sheet set
- **Push Revisions To Index** — flag sheets carrying a revision in any sheet parameter
- **Set Revision On Sheets** — apply revisions to selected sheets
- **Capitalize View Names** — auto-uppercase view titles on sheets
- **Find Code Sections** — find text notes referencing a building-code year other than the project's
- **Fix Abbreviations** — normalize abbreviations like *U.O.N.* → *UON.*
- **Apply View Filters to Templates** — push a filter into multiple view templates with one color override
- **View Pan** — translate the crop box of multiple views on a sheet by a fixed offset

### Rooms
- **Find-Replace Room#** — re-number rooms across views using an "old number" shared parameter
- **Rename Views by Room** — rename views based on closest room
- **Room Axon** — generate an isometric 3D view per selected room, scoped via section box

### Links
- **Find CAD** — categorize CAD links by 2D detail vs 3D model
- **Locate CAD File** — open the source folder of a selected CAD link
- **DWG Trace** — trace a DWG/DXF link as native Revit detail lines / filled regions
- **Sync Link Graphics** — copy Revit link graphic overrides from one view template to many

### Cloud
- **Find in ADC** — open the project's location via Autodesk Desktop Connector
- **Go To ACC** — open the project in Autodesk Construction Cloud
- **B360 Health** — Autodesk service status
- **Bluebeam Health** — Bluebeam service status

## Roadmap

- Combined **Linetype Manager** (duplicate + rename in one dialog)
- Per-tool tooltips and `help_url` on every button
- Standardized script headers across all tools

## Author

Tay Othman, AIA — architect, Boulder Associates

## License

See [LICENSE](LICENSE).
