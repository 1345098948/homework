from flask import Flask, request, jsonify, render_template
import time
import pandas as pd
from math import sqrt

app = Flask(__name__)

# 模拟数据 - 替换成实际的 CSV 文件路径
us_cities_data = pd.read_csv("us-cities.csv")


@app.route('/data/closest_cities', methods=['GET'])
def closest_cities():
    start_time = time.time()

    city_name = request.args.get('city')
    page_size = int(request.args.get('page_size', 50))
    page = int(request.args.get('page', 0))

    # 获取最近城市的模拟数据
    cities = get_closest_cities(city_name, page_size, page)

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # 转换为毫秒

    response = {
        "cities": cities,
        "computing_time": elapsed_time,
        "cache_hit": False  # 添加此属性以指示缓存状态
    }

    return jsonify(response)

@app.route("/", methods=['GET'])
def index():
    message = "Congratulations, it's a web app!"
    return render_template(
            'kk.html',
            message=message,
    )

def get_closest_cities(city_name, page_size, page):
    # 对模拟数据进行处理，根据给定城市的欧拉距离升序获取其他城市
    cities = [{"name": city["city"], "distance": calculate_distance(city_name, city["lat"], city["lng"])} for _, city in
              us_cities_data.iterrows()]
    cities.sort(key=lambda x: x["distance"])  # 按距离升序排序

    # 分页返回数据
    start_index = page * page_size
    end_index = (page + 1) * page_size
    return cities[start_index:end_index]


def calculate_distance(city_name, lat, lng):
    # 根据给定城市的欧拉距离计算其他城市的距离
    source_city = us_cities_data[us_cities_data["city"] == city_name].iloc[0]
    return sqrt((source_city["lat"] - lat) ** 2 + (source_city["lng"] - lng) ** 2)


if __name__ == '__main__':
    app.run(debug=True)
