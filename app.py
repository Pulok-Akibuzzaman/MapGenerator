from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import threading
from datetime import datetime
from map_generator import create_detailed_city_wkt, test_city_availability
import tempfile
import shutil

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Store generation status
generation_status = {}

@app.route('/')
def index():
    """Home page with form to generate WKT files"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_wkt():
    """Handle WKT generation request"""
    location = request.form.get('location', '').strip()
    detail_level = request.form.get('detail_level', 'detailed')
    map_size = request.form.get('map_size', '').strip()
    output_name = request.form.get('output_name', '').strip()
    
    if not location:
        flash('Please enter a location', 'error')
        return redirect(url_for('index'))
    
    if not output_name:
        flash('Please enter an output filename', 'error')
        return redirect(url_for('index'))
    
    # Validate map size
    try:
        map_size_int = int(map_size) if map_size else 5000
        if map_size_int < 500 or map_size_int > 50000:
            flash('Map size must be between 500 and 50,000 meters', 'error')
            return redirect(url_for('index'))
    except ValueError:
        flash('Invalid map size', 'error')
        return redirect(url_for('index'))
    
    # Create a unique job ID
    job_id = f"{output_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize status
    generation_status[job_id] = {
        'status': 'starting',
        'message': 'Initializing...',
        'location': location,
        'detail_level': detail_level,
        'map_size': map_size_int,
        'output_name': output_name,
        'file_path': None,
        'error': None
    }
    
    # Start generation in background thread
    thread = threading.Thread(target=generate_wkt_background, args=(job_id, location, detail_level, map_size_int, output_name))
    thread.daemon = True
    thread.start()
    
    return render_template('generating.html', job_id=job_id, city_name=location, detail_level=detail_level)

def generate_wkt_background(job_id, location, detail_level, map_size, output_name):
    """Background task to generate WKT file"""
    try:
        generation_status[job_id]['status'] = 'testing'
        generation_status[job_id]['message'] = f'Testing if {location} is available...'
        # Try original location
        available = test_city_availability(location)
        # If not found, try appending ', Bangladesh' as fallback for cities like Dhaka
        if not available and ',' not in location:
            fallback_location = f"{location}, Bangladesh"
            available = test_city_availability(fallback_location)
            if available:
                location = fallback_location
        if not available:
            generation_status[job_id]['status'] = 'error'
            generation_status[job_id]['error'] = f'Location "{location}" not found in OpenStreetMap database. Please try a different name or add ", Country" suffix.'
            return

        generation_status[job_id]['status'] = 'downloading'
        generation_status[job_id]['message'] = f'Downloading map data for {location} (radius: {map_size}m)...'

        # Generate WKT file with custom size
        success, counts, file_path = create_detailed_city_wkt(location, output_name, detail_level, map_size)
        
        if success and file_path:
            # Ensure file_path is absolute and correct
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            # Double-check file exists and create alternative path if needed
            if os.path.exists(file_path):
                generation_status[job_id]['status'] = 'completed'
                generation_status[job_id]['message'] = f'Successfully generated {sum(counts.values())} road segments'
                generation_status[job_id]['file_path'] = file_path
                generation_status[job_id]['counts'] = counts
            else:
                # Try to find the file in wkt_output directory
                alt_file_path = os.path.join('wkt_output', f"{output_name}.wkt")
                if os.path.exists(alt_file_path):
                    generation_status[job_id]['status'] = 'completed'
                    generation_status[job_id]['message'] = f'Successfully generated {sum(counts.values())} road segments'
                    generation_status[job_id]['file_path'] = os.path.abspath(alt_file_path)
                    generation_status[job_id]['counts'] = counts
                else:
                    generation_status[job_id]['status'] = 'error'
                    generation_status[job_id]['error'] = f'File was generated but cannot be found at {file_path} or {alt_file_path}'
        else:
            generation_status[job_id]['status'] = 'error'
            generation_status[job_id]['error'] = f'Failed to generate WKT file for {location}'
            
    except Exception as e:
        generation_status[job_id]['status'] = 'error'
        generation_status[job_id]['error'] = f'Error: {str(e)}'

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get generation status for AJAX polling"""
    status = generation_status.get(job_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/download/<job_id>')
def download_file(job_id):
    """Download generated WKT file"""
    status = generation_status.get(job_id)
    
    if not status:
        flash('Job not found', 'error')
        return redirect(url_for('index'))
    
    if status['status'] != 'completed':
        flash(f'File not ready for download. Status: {status["status"]}', 'error')
        return redirect(url_for('index'))
    
    if not status.get('file_path'):
        flash('File path not available', 'error')
        return redirect(url_for('index'))
    
    file_path = status['file_path']
    
    # Check if file exists at the recorded path
    if not os.path.exists(file_path):
        # Try alternative paths
        output_name = status['output_name']
        
        # Try in wkt_output directory with .wkt extension
        alt_path1 = os.path.join('wkt_output', f"{output_name}.wkt")
        alt_path2 = os.path.join(os.getcwd(), 'wkt_output', f"{output_name}.wkt")
        
        if os.path.exists(alt_path1):
            file_path = alt_path1
        elif os.path.exists(alt_path2):
            file_path = alt_path2
        else:
            # Create wkt_output directory if it doesn't exist
            os.makedirs('wkt_output', exist_ok=True)
            flash(f'File not found. Please regenerate the map for {status["location"]}', 'error')
            return redirect(url_for('index'))
    
    # Create a safe download filename
    output_name = status['output_name']
    download_name = f"{output_name}.wkt"
    
    try:
        return send_file(file_path, as_attachment=True, download_name=download_name)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/test_city', methods=['POST'])
def test_city():
    """AJAX endpoint to test if a location is available"""
    data = request.get_json(silent=True) or {}
    city_name = data.get('city_name', '').strip()
    
    if not city_name:
        return jsonify({'available': False, 'message': 'Location name is required'})
    
    try:
        available = test_city_availability(city_name)
        # Fallback: try appending ', Bangladesh' if not found and no country specified
        if not available and ',' not in city_name:
            fallback_city = f"{city_name}, Bangladesh"
            available = test_city_availability(fallback_city)
            if available:
                city_name = fallback_city
        if available:
            return jsonify({'available': True, 'message': f'✅ {city_name} found in OpenStreetMap'})
        else:
            return jsonify({'available': False, 'message': f'❌ {city_name} not found. Try adding country name.'})
    except Exception as e:
        return jsonify({'available': False, 'message': f'Error testing location: {str(e)}'})

@app.route('/examples')
def examples():
    """Show example cities and usage"""
    bangladesh_cities = [
        "Dhaka, Bangladesh",
        "Chittagong, Bangladesh", 
        "Bogura, Bangladesh",
        "Rangamati, Bangladesh",
        "Sylhet, Bangladesh",
        "Khulna, Bangladesh"
    ]
    
    other_cities = [
        "London, UK",
        "New York, USA",
        "Tokyo, Japan",
        "Paris, France",
        "Sydney, Australia"
    ]
    
    return render_template('examples.html', 
                         bangladesh_cities=bangladesh_cities, 
                         other_cities=other_cities)

if __name__ == '__main__':
    # Create output directory with full path
    output_dir = os.path.join(os.getcwd(), 'wkt_output')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created/verified output directory: {output_dir}")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)