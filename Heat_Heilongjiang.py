import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 解决图像中的“-”负号乱码问题

# 读取全国边界的 SHP 文件
china_boundary = gpd.read_file('CHN_adm_shp/CHN_adm1.shp')

# 筛选出湖北省的边界
heilongjiang_boundary = china_boundary[china_boundary['NAME_1'] == 'Heilongjiang']

# 读取全国城市的 SHP 文件
china_cities = gpd.read_file('CHN_adm_shp/CHN_adm2.shp')

# 筛选出湖北省的城市
heilongjiang_cities = china_cities[china_cities['NAME_1'] == 'Heilongjiang']


# 英文城市名称与中文城市名称的映射字典
city_mapping = {
    'Daqing': '大庆',
    'Daxing\'anling': '大兴安岭',
    'Harbin': '哈尔滨',
    'Hegang': '鹤岗',
    'Heihe': '黑河',
    'Jiamusi': '佳木斯',
    'Jixi': '鸡西',
    'Mudanjiang': '牡丹江',
    'Qiqihar': '齐齐哈尔',
    'Qitaihe': '七台河',
    'Shuangyashan': '双鸭山',
    'Suihua': '绥化',
    'Yichun': '伊春'
}

# 添加中文城市名称列
heilongjiang_cities['city_chinese'] = heilongjiang_cities['NAME_2'].map(city_mapping)

# 创建图形并绘制湖北省的边界
fig, ax = plt.subplots(figsize=(8, 8))
heilongjiang_boundary.plot(ax=ax, edgecolor='black', linewidth=0.5)

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
for x, y, label in zip(heilongjiang_cities.geometry.centroid.x, heilongjiang_cities.geometry.centroid.y,
                       heilongjiang_cities['city_chinese']):
    ax.text(x, y, label, fontsize=8, ha='center')


# 数据表路径
data_path = 'result_HeiLJ_经纬度.xlsx'  # 替换为您的数据表路径

# 读取数据表
df = pd.read_excel(data_path)

for column in df.columns[3:]:
    heilongjiang_city_dict = {}
    # 创建图形并绘制湖北省的边界
    fig, ax = plt.subplots(figsize=(8, 8))
    heilongjiang_boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    for x, y, label in zip(heilongjiang_cities.geometry.centroid.x, heilongjiang_cities.geometry.centroid.y,
                           heilongjiang_cities['city_chinese']):
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
        city_match = heilongjiang_cities[heilongjiang_cities['city_chinese'] == region]
        if len(city_match) == 0:
            point = Point(longitude, latitude)
            city_match = heilongjiang_cities[heilongjiang_cities.geometry.contains(point)]
        print(region)
        print(region+'转为'+city_match['city_chinese'].iloc[0])

        check_city = city_match['city_chinese'].iloc[0]
        if check_city in heilongjiang_city_dict:
            if weight > heilongjiang_city_dict[check_city]:
                heilongjiang_city_dict[check_city] = weight
            else:
                continue
        else:
            heilongjiang_city_dict[check_city] = weight
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
    # ax.set_xlim([122.4342, 135.0838])  # 根据实际地理范围设置
    # ax.set_ylim([43.4065, 53.5619])  # 根据实际地理范围设置

    # 显示图形
    # plt.show()
    timestamp = timestamp.replace(':', '_')
    timestamp = timestamp.replace(' ', '_')
    plt.savefig(f'{timestamp}.png',dpi = 200)
    ax.clear()