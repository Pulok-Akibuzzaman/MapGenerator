# Flask Map WKT Generator

A web-based application that generates Well-Known Text (WKT) files for any location using OpenStreetMap data. Built with Flask and OSMnx.

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
   cd flask_map_app
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
- GeoPandas
- PyProj
- Geopy

## Troubleshooting

**Location not found**: Try adding country name or use full location names

**Large map sizes**: Processing time increases significantly with size - start with smaller areas

**Memory errors**: Reduce map size or detail level for very large areas

## File Structure

```
flask_map_app/
├── app.py              # Main Flask application
├── map_generator.py    # WKT generation functions
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Main form interface
│   └── generating.html # Progress tracking page
└── wkt_output/         # Generated WKT files (created automatically)
```

## Development

To run in development mode:
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

The application will run on `http://localhost:5000` with debug mode enabled.