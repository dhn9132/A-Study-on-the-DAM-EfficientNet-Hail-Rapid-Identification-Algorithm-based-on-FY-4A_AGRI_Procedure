import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point

# Set the font and resolve the issue of "-" characters in plots
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# Read the SHP file of the national boundary
china_boundary = gpd.read_file('CHN_adm_shp/CHN_adm1.shp')

# Select the boundary of Heilongjiang province
heilongjiang_boundary = china_boundary[china_boundary['NAME_1'] == 'Heilongjiang']

# Read the SHP file of national cities
china_cities = gpd.read_file('CHN_adm_shp/CHN_adm2.shp')

# Select cities within Heilongjiang province
heilongjiang_cities = china_cities[china_cities['NAME_1'] == 'Heilongjiang']

# Dictionary for mapping English city names to Chinese city names
city_mapping = {
    'Daqing': 'Daqing',
    'Daxing\'anling': 'Daxing\'anling',
    'Harbin': 'Harbin',
    'Hegang': 'Hegang',
    'Heihe': 'Heihe',
    'Jiamusi': 'Jiamusi',
    'Jixi': 'Jixi',
    'Mudanjiang': 'Mudanjiang',
    'Qiqihar': 'Qiqihar',
    'Qitaihe': 'Qitaihe',
    'Shuangyashan': 'Shuangyashan',
    'Suihua': 'Suihua',
    'Yichun': 'Yichun'
}

# Add a column for Chinese city names
heilongjiang_cities['city_chinese'] = heilongjiang_cities['NAME_2'].map(city_mapping)

# Create a figure and plot the boundary of Heilongjiang province
fig, ax = plt.subplots(figsize=(8, 8))
heilongjiang_boundary.plot(ax=ax, edgecolor='black', linewidth=0.5)

# Add city name labels
for x, y, label in zip(heilongjiang_cities.geometry.centroid.x, heilongjiang_cities.geometry.centroid.y,
                       heilongjiang_cities['city_chinese']):
    ax.text(x, y, label, fontsize=8, ha='center')

# Data table path
data_path = 'result_HeiLJ_lonlats.xlsx'  # Replace with your data table path

# Read the data table
df = pd.read_excel(data_path)

for column in df.columns[3:]:
    heilongjiang_city_dict = {}
    # Create a figure and plot the boundary of Heilongjiang province
    fig, ax = plt.subplots(figsize=(8, 8))
    heilongjiang_boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    # Add city name labels
    for x, y, label in zip(heilongjiang_cities.geometry.centroid.x, heilongjiang_cities.geometry.centroid.y,
                           heilongjiang_cities['city_chinese']):
        ax.text(x, y, label, fontsize=8, ha='center')

    timestamp = column
    data = df[['region', 'Lon', 'Lat', column]].dropna()

    # Define a color mapping based on weight
    rgb = {
        0: '#FFFFFF', 1: '#87CEEB', 2: '#90EE90', 3: '#000080',
        4: '#800080', 5: '#FFA500', 6: '#FFC0CB', 7: '#FF0000',
        8: '#8B0000'
    }

    # Determine cities based on data and change their colors
    for d in data.iterrows():
        longitude = d[1]['Lon']
        latitude = d[1]['Lat']
        region = d[1]['region']
        weight = d[1][column]
        # Find a matching city
        city_match = heilongjiang_cities[heilongjiang_cities['city_chinese'] == region]
        if len(city_match) == 0:
            point = Point(longitude, latitude)
            city_match = heilongjiang_cities[heilongjiang_cities.geometry.contains(point)]
        print(region)
        print(region + ' changed to ' + city_match['city_chinese'].iloc[0])

        check_city = city_match['city_chinese'].iloc[0]
        if check_city in heilongjiang_city_dict:
            if weight > heilongjiang_city_dict[check_city]:
                heilongjiang_city_dict[check_city] = weight
            else:
                continue
        else:
            heilongjiang_city_dict[check_city] = weight
        # If a matching city is found
        if not city_match.empty:
            city_row = city_match.iloc[0]
            city_polygon = city_row.geometry
            if city_polygon.geom_type == 'Polygon':
                coords = city_polygon.exterior.coords
                x, y = zip(*coords)
                color = rgb.get(weight, '#FFFFFF')
                ax.fill(x, y, color=color, alpha=1)  # Fill the polygon area
                ax.plot(x, y, color='black', linewidth=1.5)  # Draw boundary lines, make them thicker
            elif city_polygon.geom_type == 'MultiPolygon':
                for geom in city_polygon:
                    coords = geom.exterior.coords
                    x, y = zip(*coords)
                    color = rgb.get(weight, '#FFFFFF')
                    ax.fill(x, y, color=color, alpha=1)  # Fill the polygon area
                    ax.plot(x, y, color='black', linewidth=1.5)  # Draw boundary lines, make them thicker

    # Create a legend
    ax_legend = fig.add_axes([0.15, 0.5, 0.2, 0.2])  # Adjust position and size
    ax_legend.set_axis_off()

    # Add legend items
    for i, (weight, color) in enumerate(rgb.items()):
        ax_legend.add_patch(plt.Rectangle((0.2, i / 8 - 0.1), 0.1, 0.1, color=color))
        ax_legend.text(0.35, i / 8 - 0.04, 'Weight ' + str(weight), fontsize=8, va='center')

    # Set the plot's geographic range
    # ax.set_xlim([122.4342, 135.0838])  # Set based on the actual geographic range
    # ax.set_ylim([43.4065, 53.5619])  # Set based on the actual geographic range

    # Save the plot as an image
    timestamp = timestamp.replace(':', '_')
    timestamp = timestamp.replace(' ', '_')
    plt.savefig(f'{timestamp}.png', dpi=200)
    ax.clear()
