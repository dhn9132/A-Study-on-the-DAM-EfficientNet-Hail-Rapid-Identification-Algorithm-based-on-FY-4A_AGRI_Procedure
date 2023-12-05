import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point

plt.rcParams["font.sans-serif"] = ["SimHei"]  # Set the font
plt.rcParams["axes.unicode_minus"] = False  # Resolve the issue of "-" characters in plots

# Read the SHP file of the national boundary
china_boundary = gpd.read_file('CHN_adm_shp/CHN_adm1.shp')

# Select the boundary of Hubei province
hubei_boundary = china_boundary[china_boundary['NAME_1'] == 'Hubei']

# Read the SHP file of national cities
china_cities = gpd.read_file('CHN_adm_shp/CHN_adm2.shp')

# Select cities within Hubei province
hubei_cities = china_cities[china_cities['NAME_1'] == 'Hubei']

# Dictionary for mapping English city names to Chinese city names
city_mapping = {
    'Enshi Tujia and Miao': 'Enshi Tujia and Miao Autonomous Prefecture',
    'Ezhou': 'Ezhou City',
    'Huanggang': 'Huanggang City',
    'Huangshi': 'Huangshi City',
    'Jingmen': 'Jingmen City',
    'Jingzhou': 'Jingzhou City',
    'Qianjiang': 'Qianjiang City',
    'Shennongjia': 'Shennongjia Forest District',
    'Shiyan': 'Shiyan City',
    'Suizhou Shi': 'Suizhou City',
    'Tianmen': 'Tianmen City',
    'Wuhan': 'Wuhan City',
    'Xiangfan': 'Xiangyang City',
    'Xianning': 'Xianning City',
    'Xiantao': 'Xiantao City',
    'Xiaogan': 'Xiaogan City',
    'Yichang': 'Yichang City'
}

# Add a column for Chinese city names
hubei_cities['city_chinese'] = hubei_cities['NAME_2'].map(city_mapping)

# Create a figure and plot the boundary of Hubei province
fig, ax = plt.subplots(figsize=(8, 8))
hubei_boundary.plot(ax=ax, edgecolor='black', linewidth=0.5)

# Add city name labels
for x, y, label in zip(hubei_cities.geometry.centroid.x, hubei_cities.geometry.centroid.y,
                       hubei_cities['city_chinese']):
    ax.text(x, y, label, fontsize=8, ha='center')

# Data table path
data_path = 'result_HuB_lonlats.xlsx'  # Replace with your data table path

# Read the data table
df = pd.read_excel(data_path)

for column in df.columns[3:]:
    hubei_city_dict = {}
    # Create a figure and plot the boundary of Hubei province
    fig, ax = plt.subplots(figsize=(8, 8))
    hubei_boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    # Add city name labels
    for x, y, label in zip(hubei_cities.geometry.centroid.x, hubei_cities.geometry.centroid.y,
                           hubei_cities['city_chinese']):
        ax.text(x, y, label, fontsize=8, ha='center')

    timestamp = column
    data = df[['region', 'Lon', 'Lat', column]].dropna()

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
        city_match = hubei_cities[hubei_cities['city_chinese'] == region]
        if len(city_match) == 0:
            # If region name doesn't match a city name, find the city based on coordinates
            point = Point(longitude, latitude)
            city_match = hubei_cities[hubei_cities.geometry.contains(point)]
        check_city = city_match['city_chinese'].iloc[0]
        print(region + ' changed to ' + check_city)
        if check_city in hubei_city_dict:
            if weight > hubei_city_dict[check_city]:
                hubei_city_dict[check_city] = weight
            else:
                continue
        else:
            hubei_city_dict[check_city] = weight
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
    ax.set_xlim([107.5, 117.0])  # Set based on the actual geographic range
    ax.set_ylim([28.0, 34.5])  # Set based on the actual geographic range

    # Save the plot as an image
    timestamp = timestamp.replace(':', '_')
    timestamp = timestamp.replace(' ', '_')
    plt.savefig(f'{timestamp}.png')
