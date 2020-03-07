import sys
import os
import pandas as pd
import geopy
import json

# Combine monthly data into one data frame
data = {}
in_dir = sys.path[0] + '/assets/eia_monthly_imports_oil_gas_2019/'
for file in os.listdir(in_dir):
    in_file = in_dir + file
    xl_file = pd.read_excel(in_file)
    time = file.split('_')[1].split('.')[0]
    data[time] = xl_file
df = pd.concat(data)

# ['RPT_PERIOD', 'R_S_NAME', 'LINE_NUM', 'PROD_CODE', 'PROD_NAME', 'PORT_CODE', 'PORT_CITY', 'PORT_STATE',
# 'PORT_PADD', 'GCTRY_CODE', 'CNTRY_NAME', 'QUANTITY', 'SULFUR', 'APIGRAVITY', 'PCOMP_RNAM', 'PCOMP_SITEID',
# 'PCOMP_SNAM', 'PCOMP_STAT', 'STATE_NAME', 'PCOMP_PADD']

# Create GeoJSON FeatureCollection object to store data as geographic features
geojson = {
    "type": "FeatureCollection",
    "name": "nodes",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }},
    "features": []
}

# Create new field with full port city and state names for more accurate geocoding results
df['PORT_CITY_'] = df['PORT_CITY'].str.split(',').str[0]
df['PORT_CITY_STATE'] = df['PORT_CITY_'].str.cat(df['PORT_STATE'], sep=', ')

# Create a list of all places to geocode
places = list(dict.fromkeys(df['PORT_CITY_STATE'])) + list(dict.fromkeys(df['CNTRY_NAME']))

# Initialize geocoder
locator = geopy.Nominatim(user_agent='myGeocoder', timeout=3)

for place in places:
    # Use codes for ports and countries as unique node ID's
    if ',' in place:
        node = df[df['PORT_CITY_STATE'] == place].mean()['PORT_CODE'].astype(int)
    else:
        node = df[df['CNTRY_NAME'] == place].mean()['GCTRY_CODE'].astype(int)
    # Handle exceptions for place names that were detected incorrectly by geocoder
    if place == 'PT CANAVERAL, FLORIDA':
        place = 'PORT CANAVERAL, FLORIDA'
    # Geocode coordinates for places
    location = locator.geocode(place)
    # Handle exceptions for place names that could not be detected by geocoder
    if not location:
        if place == 'CHAMPL-RS PT, NEW YORK':
            place = 'CHAMPLAIN-ROUSES POINT, NEW YORK'
        elif place == 'INTER. FALLS, MINNESOTA':
            place = 'INTERNATIONAL FALLS, MINNESOTA'
        elif place == 'BUFF-NIAG FL, NEW YORK':
            place = 'BUFFALO-NIAGARA FALLS, NEW YORK'
        elif place == 'HIG-SPRG/ALB, VERMONT':
            place = 'HIGHGATE SPRINGS-ALBURG, VERMONT'
        elif place == 'HONOLU/PEARL, HAWAII':
            place = 'PEARL HARBOR, HAWAII'
        elif place == 'CHRISTIANSTD, VIRGIN ISLANDS':
            place = 'CHRISTIANSTED, VIRGIN ISLANDS'
        elif place == 'NAWILIWV-POR, HAWAII':
            place = 'NAWILIWILI HARBOR, HAWAII'
        elif place == 'SANPABLO BAY, CALIFORNIA':
            place = 'SAN PABLO BAY, CALIFORNIA'
        elif place == 'SALT LK CTY, UTAH':
            place = 'SALT LAKE CITY, UTAH'
        elif place == 'NATRONA APRT, WYOMING':
            place = 'CASPER/NATRONA COUNTY INTERNATIONAL AIRPORT, WYOMING'
        elif place == 'SAULT ST-MAR, MICHIGAN':
            place = 'SAULT STE. MARIE, MICHIGAN'
        elif place == 'RCHMD-PETERS, VIRGINIA':
            place = 'RICHMOND-PETERSBURG, VIRGINIA'
        elif place == 'DALTON CACHE, ALASKA':
            place = 'HAINES, ALASKA'
        elif place == 'SAN FRAN INT AP, CALIFORNIA':
            place = 'SAN FRANCISCO INTERNATIONAL AIRPORT, CALIFORNIA'
        elif place == 'BEECHERFALLS, VERMONT':
            place = 'BEECHER FALLS, VERMONT'
        elif place == 'MACKINAC ISL, MICHIGAN':
            place = 'MACKINAC ISLAND, MICHIGAN'
        elif place == 'CORPUS CHRIS, TEXAS':
            place = 'CORPUS CHRISTI, TEXAS'
        elif place == 'SANFRANCISCO, CALIFORNIA':
            place = 'SAN FRANCISCO, CALIFORNIA'
        elif place == 'NORTHGATE, NORTH DAKOTA':
            place = 'BURKE COUNTY, NORTH DAKOTA'
        location = locator.geocode(place)
    if not location:
        print('Geocode failed: ' + place)

    # Create GeoJSON feature and append to GeoJSON FeatureCollection
    feature = {
        "type": "Feature",
        "id": int(node),
        "properties": {
            "name": place
        },
        "geometry": {
            "type": "Point",
            "coordinates": [location.longitude, location.latitude]
        }
    }
    geojson['features'].append(feature)

# Save GeoJSON file
with open('assets/nodes.geojson', 'w') as f:
    json.dump(geojson, f)
print('GeoJSON created: assets/nodes.geojson')

# Summarize combined data into new data frame
# Create new field with both port city and country of origin information, concatenating their unique codes
df['TARGET_SOURCE'] = df['PORT_CODE'].map(str) + '-' + df['GCTRY_CODE'].map(str)
# Create list of all target-source pairs
target_source_pairs = list(dict.fromkeys(df['TARGET_SOURCE']))
links = {}
for target_source in target_source_pairs:
    link = pd.DataFrame(columns=['target', 'source', 'flow', 'target_name', 'source_name', 'target_source'])
    link = link.append({'target': target_source.split('-')[0],
                        'source': target_source.split('-')[1],
                        'flow': df[df['TARGET_SOURCE'] == target_source].sum()['QUANTITY'],
                        'target_name': df[df['TARGET_SOURCE'] == target_source]['PORT_CITY_STATE'].values[0],
                        'source_name': df[df['TARGET_SOURCE'] == target_source]['CNTRY_NAME'].values[0],
                        'target_source': target_source
                        }, ignore_index=True)
    links[target_source] = link
df = pd.concat(links)
df.to_csv('assets/links.csv', index=False)
print('CSV created: assets/links.csv')

print('Data pre-processing complete!')
