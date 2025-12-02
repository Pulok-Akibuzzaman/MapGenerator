# Map Generator

A web-based application that generates Well-Known Text (WKT) files for any location using OpenStreetMap data. Built with Flask and OSMnx.

This tool allows users to easily create WKT (Well-Known Text) files containing road network data for any location worldwide. The generated files can be used in GIS applications, spatial databases, and other mapping software that supports the WKT format.

## Quick Start

1. Install Python 3.8+ and clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python app.py`
4. Open http://localhost:5000 in your browser
5. Enter a location (e.g., "Paris, France") and generate your WKT file!

## Features

- **Global Coverage**: Generate maps for any location worldwide
- **Customizable Map Size**: Set radius from 500m to 50km
- **Multiple Detail Levels**: Choose from major roads, detailed roads, or complete road networks
- **Custom Output Names**: Name your WKT files as needed
- **Real-time Progress**: Live updates during map generation
- **Interactive Interface**: Test location availability before generation

## Installation

1. **Clone or download the project**:
   ```bash
   cd MapGenerator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Flask application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and go to:
   ```
   http://localhost:5000
   ```

3. **Fill out the form**:
   - **Location**: Enter any city name (e.g., "London, UK", "Dhaka, Bangladesh")
   - **Map Size**: Choose radius in meters (500-50,000m)
   - **Detail Level**: Select road detail level
   - **Output Name**: Enter filename for your WKT file

4. **Generate and Download**: Click "Generate WKT Map" and wait for processing to complete, then download your file.

## Detail Levels

- **Major Roads**: Highways, motorways, primary roads
- **Detailed**: Includes residential streets and tertiary roads  
- **Complete**: All driveable roads including service roads

## File Output

Generated WKT files include:
- Header with location and generation details
- Road type breakdown and statistics
- UTM coordinate system information
- One LINESTRING per road segment

## Example Locations

### Bangladesh Cities:
- Dhaka, Bangladesh
- Chittagong, Bangladesh
- Sylhet, Bangladesh
- Khulna, Bangladesh

### International Cities:
- London, UK
- New York, USA
- Tokyo, Japan
- Paris, France

## Technical Details

- Built with Flask web framework
- Uses OSMnx for OpenStreetMap data retrieval
- Converts coordinates to appropriate UTM zones
- Generates standards-compliant WKT format
- Background processing with real-time status updates

## Requirements

- Python 3.8+
- Flask 2.3+
- OSMnx 1.6+
- GeoPandas 0.14+
- PyProj 3.6+
- Geopy 2.4+

All dependencies are listed in `requirements.txt` and will be installed automatically with `pip install -r requirements.txt`.

## Troubleshooting

**Location not found**: 
- Try adding country name or use full location names
- Examples: "London, UK" instead of just "London"
- Use official city names when possible

**Large map sizes**: 
- Processing time increases significantly with size
- Start with smaller areas (500m-5km) for testing
- Large areas (>20km) may take several minutes

**Memory errors**: 
- Reduce map size or detail level for very large areas
- Close other applications to free up memory
- Consider using "Major Roads" detail level for large areas

**Application won't start**:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python 3.8+ is installed
- Verify Flask installation: `python -c "import flask; print(flask.__version__)"`

## File Structure

```
MapGenerator/
├── app.py              # Main Flask application
├── map_generator.py    # WKT generation functions
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Main form interface
│   └── generating.html # Progress tracking page
└── cache/              # Cached data files (created automatically)
```

## Development

To run in development mode:
```bash
# For Linux/Mac
export FLASK_ENV=development
python app.py

# For Windows PowerShell
$env:FLASK_ENV="development"
python app.py

# For Windows Command Prompt
set FLASK_ENV=development
python app.py
```

The application will run on `http://localhost:5000` with debug mode enabled.

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.# MapGenerator-MapBD-
