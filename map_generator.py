def test_city_availability(city_name):
    """Test if a city can be found by geocoding using Nominatim (OpenStreetMap). Returns True if found, False otherwise."""
    try:
        from geopy.geocoders import Nominatim
        print(f"[DEBUG] Searching for city: {city_name} using Nominatim")
        geolocator = Nominatim(user_agent="map_app")
        location = geolocator.geocode(city_name)
        print(f"[DEBUG] Geocoder result for '{city_name}': {location}")
        if not location and city_name.lower() == 'london':
            location = geolocator.geocode('London, England, UK')
            print(f"[DEBUG] Fallback to 'London, England, UK': {location}")
        if not location and city_name.lower() == 'london, uk':
            location = geolocator.geocode('London, United Kingdom')
            print(f"[DEBUG] Fallback to 'London, United Kingdom': {location}")
        return location is not None
    except Exception as e:
        print(f"[DEBUG] Exception in test_city_availability: {e}")
        return False

# Map Generator Module for Flask App
# Extracted from Map.py for web-based usage

import osmnx as ox
import os
from collections import Counter
from pyproj import Transformer
import re

def get_utm_zone(lat, lon):
    """Get appropriate UTM zone for given coordinates"""
    if lat >= 0:
        utm_zone = int((lon + 180) / 6) + 1
        epsg_code = f"326{utm_zone:02d}"  # Northern hemisphere
    else:
        utm_zone = int((lon + 180) / 6) + 1
        epsg_code = f"327{utm_zone:02d}"  # Southern hemisphere
    return f"EPSG:{epsg_code}"

def create_detailed_city_wkt(city_name, output_filename, detail_level='detailed', custom_size=None, save_path='wkt_output'):
    """
    Create detailed WKT files for cities with customizable map size

    Args:
        city_name: Name of the city/location
        output_filename: Base filename for output
        detail_level: 'major', 'detailed', 'complete'
        custom_size: Distance in meters from center (default: auto-detected)
        save_path: Directory to save the WKT file (default: 'wkt_output')
    """
    try:
        print(f"📍 Downloading detailed map for: {city_name}")

        if detail_level == 'major':
            custom_filter = '["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link"]'
            road_desc = "major"
        elif detail_level == 'detailed':
            custom_filter = '["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|residential|unclassified"]'
            road_desc = "detailed"
        else:  # complete
            custom_filter = None
            road_desc = "complete"

        if custom_size:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="map_app")
            def resolve_location(name):
                loc = geolocator.geocode(name)
                if loc is not None and hasattr(loc, '__await__'):
                    import asyncio
                    loc = asyncio.run(loc)
                import types
                if isinstance(loc, types.CoroutineType):
                    return None
                return loc

            location = resolve_location(city_name)
            if not location and city_name.lower() == 'london':
                location = resolve_location('London, England, UK')
            if not location and city_name.lower() == 'london, uk':
                location = resolve_location('London, United Kingdom')
            if not location:
                candidates = geolocator.geocode(city_name, exactly_one=False, addressdetails=True, limit=5)
                if candidates and hasattr(candidates, '__await__'):
                    import asyncio
                    candidates = asyncio.run(candidates)
                import types
                if isinstance(candidates, types.CoroutineType):
                    candidates = None
                suggestions = []
                if candidates:
                    for cand in candidates:
                        if hasattr(cand, 'address'):
                            suggestions.append(cand.address)
                if suggestions:
                    raise ValueError(f"Location '{city_name}' not found. Did you mean: {suggestions}?")
                else:
                    raise ValueError(f"Location '{city_name}' not found. Try a more specific name, e.g. 'London, England, UK'.")
            if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                point = (location.latitude, location.longitude)
            else:
                raise ValueError(f"Location object missing latitude/longitude for '{city_name}'")
            if custom_filter:
                G = ox.graph_from_point(point, dist=custom_size, custom_filter=custom_filter)
            else:
                G = ox.graph_from_point(point, dist=custom_size, network_type='drive')
        else:
            if custom_filter:
                G = ox.graph_from_place(city_name, custom_filter=custom_filter)
            else:
                G = ox.graph_from_place(city_name, network_type='drive')

        nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
        print(f"   📊 Found {len(edges_gdf)} road segments")
        bounds = edges_gdf.total_bounds
        center_lon = (bounds[0] + bounds[2]) / 2
        center_lat = (bounds[1] + bounds[3]) / 2
        utm_epsg = get_utm_zone(center_lat, center_lon)
        print(f"   🗺️  Using coordinate system: {utm_epsg}")
        edges_utm = edges_gdf.to_crs(utm_epsg)
        highway_counts = Counter()
        total_segments = 0

        # Create output directory
        os.makedirs(save_path, exist_ok=True)

        # Prepare WKT file
        wkt_file = os.path.join(save_path, f"{output_filename}.wkt")

        # Count road types and prepare data
        linestrings = []
        for idx, row in edges_utm.iterrows():
            highway_type = row.get('highway', 'unknown')
            if isinstance(highway_type, list):
                highway_type = highway_type[0] if highway_type else 'unknown'

            highway_counts[highway_type] += 1
            total_segments += 1

            # Get the geometry as WKT and format coordinates
            geom_wkt = row.geometry.wkt

            # Round coordinates to 2 decimal places
            def round_coords(match):
                x, y = match.groups()
                return f"{float(x):.2f} {float(y):.2f}"

            # Replace coordinate pairs in WKT string
            geom_wkt = re.sub(r'(\d+\.\d+)\s+(\d+\.\d+)', round_coords, geom_wkt)
            try:
                print(f"Downloading detailed map for: {city_name}")

                if detail_level == 'major':
                    custom_filter = '["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link"]'
                    road_desc = "major"
                elif detail_level == 'detailed':
                    custom_filter = '["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|residential|unclassified"]'
                    road_desc = "detailed"
                else:  # complete
                    custom_filter = None
                    road_desc = "complete"

                # Use OSMnx's place search directly for standard city names
                if custom_filter:
                    G = ox.graph_from_place(city_name, custom_filter=custom_filter)
                else:
                    G = ox.graph_from_place(city_name, network_type='drive')

                if G is None or len(G.nodes) == 0:
                    print(f"Error: No road network found for '{city_name}'. Try a more specific or different name.")
                    return False, {}, None

                print(f"   Found {len(G.nodes)} nodes and {len(G.edges)} edges in the network.")

                nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
                bounds = edges_gdf.total_bounds
                center_lon = (bounds[0] + bounds[2]) / 2
                center_lat = (bounds[1] + bounds[3]) / 2
                utm_epsg = get_utm_zone(center_lat, center_lon)
                print(f"   Using coordinate system: {utm_epsg}")
                edges_utm = edges_gdf.to_crs(utm_epsg)
                highway_counts = Counter()
                total_segments = 0

                # Create output directory
                os.makedirs(save_path, exist_ok=True)

                # Prepare WKT file
                wkt_file = os.path.join(save_path, f"{output_filename}.wkt")

                # Count road types and prepare data
                linestrings = []
                for idx, row in edges_utm.iterrows():
                    highway_type = row.get('highway', 'unknown')
                    if isinstance(highway_type, list):
                        highway_type = highway_type[0] if highway_type else 'unknown'

                    highway_counts[highway_type] += 1
                    total_segments += 1

                    # Get the geometry as WKT and format coordinates
                    geom_wkt = row.geometry.wkt

                    # Round coordinates to 2 decimal places
                    def round_coords(match):
                        x, y = match.groups()
                        return f"{float(x):.2f} {float(y):.2f}"

                    # Replace coordinate pairs in WKT string
                    geom_wkt = re.sub(r'(\d+\.\d+)\s+(\d+\.\d+)', round_coords, geom_wkt)
                    linestrings.append(geom_wkt)

                # Write the file with exact format
                with open(wkt_file, 'w') as f:
                    # Header matching your format
                    f.write(f"# {road_desc.title()} roads WKT data for {city_name}\n")
                    f.write(f"# Road types: {road_desc}\n")
                    f.write(f"# Coordinate system: {utm_epsg}\n")
                    if custom_size:
                        f.write(f"# Map size: {custom_size}m radius from center\n")
                    f.write(f"# Generated {total_segments} road segments\n")
                    f.write("# Road type breakdown:\n")

                    # Sort highway types for consistent output
                    for highway_type in sorted(highway_counts.keys()):
                        count = highway_counts[highway_type]
                        f.write(f"#   {highway_type}: {count} segments\n")

                    f.write("# Format: One LINESTRING per line\n")

                    # Write all linestrings
                    for linestring in linestrings:
                        f.write(f"{linestring}\n")

                print(f"Success: {city_name} ({detail_level}): {total_segments} road segments")
                print(f"   File: {wkt_file}")
                print(f"   Road types found: {len(highway_counts)} different types")

                return True, highway_counts, wkt_file

            except Exception as e:
                print(f"Failed to process {city_name}: {e}")
                return False, {}, None
        G = ox.graph_from_point(point, dist=1000, network_type='drive')  # Small area test
        print(f"✅ {city_name} found! {len(G.nodes)} nodes in test area")
        return True
    except Exception as e:
        print(f"❌ {city_name} not found: {str(e)[:100]}...")
        return False

def get_map_bounds(city_name):
    """Get the geographical bounds of a city"""
    try:
        # Get a small sample to find bounds
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="map_app")
        def resolve_location(name):
            loc = geolocator.geocode(name)
            if loc is not None and hasattr(loc, '__await__'):
                import asyncio
                loc = asyncio.run(loc)
            import types
            if isinstance(loc, types.CoroutineType):
                return None
            return loc

        location = resolve_location(city_name)
        if not location and city_name.lower() == 'london':
            location = resolve_location('London, England, UK')
        if not location and city_name.lower() == 'london, uk':
            location = resolve_location('London, United Kingdom')
        if not location:
            candidates = geolocator.geocode(city_name, exactly_one=False, addressdetails=True, limit=5)
            if candidates and hasattr(candidates, '__await__'):
                import asyncio
                candidates = asyncio.run(candidates)
            import types
            if isinstance(candidates, types.CoroutineType):
                candidates = None
            suggestions = []
            if candidates:
                for cand in candidates:
                    if hasattr(cand, 'address'):
                        suggestions.append(cand.address)
            if suggestions:
                raise ValueError(f"Location '{city_name}' not found. Did you mean: {suggestions}?")
            else:
                raise ValueError(f"Location '{city_name}' not found. Try a more specific name, e.g. 'London, England, UK'.")
        if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
            point = (location.latitude, location.longitude)
        else:
            raise ValueError(f"Location object missing latitude/longitude for '{city_name}'")
        G = ox.graph_from_point(point, dist=2000, network_type='drive')
        nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
        bounds = edges_gdf.total_bounds
        
        # Calculate approximate size
        from geopy.distance import geodesic
        
        # Calculate width and height in km
        width_km = geodesic((bounds[1], bounds[0]), (bounds[1], bounds[2])).kilometers
        height_km = geodesic((bounds[1], bounds[0]), (bounds[3], bounds[0])).kilometers
        
        return {
            'bounds': bounds.tolist(),
            'width_km': round(width_km, 2),
            'height_km': round(height_km, 2),
            'center_lat': (bounds[1] + bounds[3]) / 2,
            'center_lon': (bounds[0] + bounds[2]) / 2
        }
    except Exception as e:
        return None