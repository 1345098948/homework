from flask import Flask, request, jsonify, render_template
import time
import pandas as pd
from math import sqrt
from sklearn.cluster import KMeans

app = Flask(__name__)

# 模拟数据 - 替换成实际的 CSV 文件路径
us_cities_data = pd.read_csv("us-cities.csv")
# Load data from CSV files


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

# Endpoint to handle the KNN clustering request
@app.route('/data/knn_reviews/stat/knn_reviews', methods=['GET'])
def knn_reviews():
    cities_df = pd.read_csv('us-cities.csv')
    reviews_df = pd.read_csv('amazon-reviews.csv')
    try:
        # Get request parameters
        classes = int(request.args.get('classes'))
        k = int(request.args.get('k'))
        words = int(request.args.get('words'))

        # Extract relevant data for clustering
        X = cities_df[['lat', 'lng', 'population']]

        # Use KMeans for clustering
        kmeans = KMeans(n_clusters=classes, random_state=42)
        cities_df['cluster'] = kmeans.fit_predict(X)

        # Process clusters and prepare response
        results = []
        for cluster_id in range(classes):
            cluster_mask = (cities_df['cluster'] == cluster_id)
            cluster_cities = cities_df.loc[cluster_mask, 'city'].tolist()
            center_city = get_center_city(cluster_cities)
            popular_words = get_popular_words(cluster_cities, words)
            weighted_avg_score = calculate_weighted_avg_score(reviews_df, cluster_cities)

            result = {
                'class_id': cluster_id,
                'center_city': center_city,
                'cities': cluster_cities,
                'popular_words': popular_words,
                'weighted_avg_score': weighted_avg_score,
            }

            results.append(result)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_center_city(cities):
    # Replace this with your logic to determine the center city
    return cities[0] if cities else None

def get_popular_words(cities, num_words):
    # Replace this with your logic to determine popular words
    return ['i', 'the', 'me']  # Placeholder data

def calculate_weighted_avg_score(reviews_df, cluster_cities):
    cities_df = pd.read_csv('us-cities.csv')
    reviews_df = pd.read_csv('amazon-reviews.csv')
    # Merge reviews_df with cities_df to get the population information
    merged_df = pd.merge(reviews_df, cities_df[['city', 'population']], on='city', how='inner')

    # Filter for reviews of cities in the current cluster
    cluster_reviews = merged_df[merged_df['city'].isin(cluster_cities)]

    # Calculate weighted average score
    weighted_avg_score = (cluster_reviews['score'] * cluster_reviews['population']).sum() / cluster_reviews[
        'population'].sum()

    return weighted_avg_score
if __name__ == '__main__':
    app.run(debug=True)
