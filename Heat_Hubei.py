import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 解决图像中的“-”负号乱码问题

# 读取全国边界的 SHP 文件
china_boundary = gpd.read_file('CHN_adm_shp/CHN_adm1.shp')

# 筛选出湖北省的边界
hubei_boundary = china_boundary[china_boundary['NAME_1'] == 'Hubei']

# 读取全国城市的 SHP 文件
china_cities = gpd.read_file('CHN_adm_shp/CHN_adm2.shp')

# 筛选出湖北省的城市
hubei_cities = china_cities[china_cities['NAME_1'] == 'Hubei']

# 英文城市名称与中文城市名称的映射字典
city_mapping = {
    'Enshi Tujia and Miao': '恩施土家族苗族自治州',
    'Ezhou': '鄂州市',
    'Huanggang': '黄冈市',
    'Huangshi': '黄石市',
    'Jingmen': '荆门市',
    'Jingzhou': '荆州市',
    'Qianjiang': '潜江市',
    'Shennongjia': '神农架林区',
    'Shiyan': '十堰市',
    'Suizhou Shi': '随州市',
    'Tianmen': '天门市',
    'Wuhan': '武汉市',
    'Xiangfan': '襄阳市',
    'Xianning': '咸宁市',
    'Xiantao': '仙桃市',
    'Xiaogan': '孝感市',
    'Yichang': '宜昌市'
}

# 添加中文城市名称列
hubei_cities['city_chinese'] = hubei_cities['NAME_2'].map(city_mapping)

# 创建图形并绘制湖北省的边界
fig, ax = plt.subplots(figsize=(8, 8))
hubei_boundary.plot(ax=ax, edgecolor='black', linewidth=0.5)

# # 创建图形并绘制湖北省的城市边界
# for index, row in hubei_cities.iterrows():
#     color = '#FFFFFF'  # 默认颜色为白色
#     polygon = row.geometry
#     if polygon.geom_type == 'Polygon':
#         coords = polygon.exterior.coords
#         x, y = zip(*coords)
#         ax.fill(x, y, color=color, alpha=1)  # 填充多边形区域
#         ax.plot(x, y, color='black', linewidth=1.5)  # 绘制边界线条，加粗线条
#     elif polygon.geom_type == 'MultiPolygon':
#         for geom in polygon:
#             coords = geom.exterior.coords
#             x, y = zip(*coords)
#             ax.fill(x, y, color=color, alpha=1)  # 填充多边形区域
#             ax.plot(x, y, color='black', linewidth=1.5)  # 绘制边界线条，加粗线条

# 添加城市名称标签
for x, y, label in zip(hubei_cities.geometry.centroid.x, hubei_cities.geometry.centroid.y,
                       hubei_cities['city_chinese']):
    ax.text(x, y, label, fontsize=8, ha='center')


# 数据表路径
data_path = 'result_HuB_经纬度.xlsx'  # 替换为您的数据表路径

# 读取数据表
df = pd.read_excel(data_path)

for column in df.columns[3:]:
    hubei_city_dict = {}
    # 创建图形并绘制湖北省的边界
    fig, ax = plt.subplots(figsize=(8, 8))
    hubei_boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

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

    # 根据数据确定城市并更改颜色
    for d in data.iterrows():
        longitude = d[1]['Lon']
        latitude = d[1]['Lat']
        region = d[1]['region']
        weight = d[1][column]
        # 查找城市
        city_match = hubei_cities[hubei_cities['city_chinese'] == region]
        if len(city_match) == 0:
            # 如果地区名与城市名不匹配，则根据经纬度查找所属城市
            # point = {'type': 'Point', 'coordinates': (longitude, latitude)}
            # city_match = hubei_cities[hubei_cities.geometry.contains(point)]
            point = Point(longitude, latitude)
            city_match = hubei_cities[hubei_cities.geometry.contains(point)]
        check_city = city_match['city_chinese'].iloc[0]
        print(region+'变为'+check_city)
        if check_city in hubei_city_dict:
            if weight > hubei_city_dict[check_city]:
                hubei_city_dict[check_city] = weight
            else:
                continue
        else:
            hubei_city_dict[check_city] = weight
        # 如果找到匹配的城市
        if not city_match.empty:
            city_row = city_match.iloc[0]
            city_polygon = city_row.geometry
            if city_polygon.geom_type == 'Polygon':
                coords = city_polygon.exterior.coords
                x, y = zip(*coords)
                color = rgb.get(weight, '#FFFFFF')
                ax.fill(x, y, color=color, alpha=1)  # 填充多边形区域
                ax.plot(x, y, color='black', linewidth=1.5)  # 绘制边界线条，加粗线条
            elif city_polygon.geom_type == 'MultiPolygon':
                 for geom in city_polygon:
                     coords = geom.exterior.coords
                     x, y = zip(*coords)
                     color = rgb.get(weight, '#FFFFFF')
                     ax.fill(x, y, color=color, alpha=1)  # 填充多边形区域
                     ax.plot(x, y, color='black', linewidth=1.5)  # 绘制边界线条，加粗线条

    # 创建图例
    ax_legend = fig.add_axes([0.15, 0.5, 0.2, 0.2])  # 调整位置和大小
    ax_legend.set_axis_off()

    # 添加图例项
    for i, (weight, color) in enumerate(rgb.items()):
        ax_legend.add_patch(plt.Rectangle((0.2, i / 8 - 0.1), 0.1, 0.1, color=color))
        ax_legend.text(0.35, i / 8-0.04, '权值'+str(weight), fontsize=8, va='center')

    # 设置图形范围
    ax.set_xlim([107.5, 117.0])  # 根据实际地理范围设置
    ax.set_ylim([28.0, 34.5])  # 根据实际地理范围设置

    # 显示图形
    # plt.show()
    timestamp = timestamp.replace(':', '_')
    timestamp = timestamp.replace(' ', '_')
    plt.savefig(f'{timestamp}.png')
    ax.clear()