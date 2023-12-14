from flask import Flask, render_template, request, jsonify
import pandas as pd
import csv


app = Flask(__name__)



def fetch_data(city_name = None, include_header = False, exact_match = False):
    with open("us-cities.csv") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_id = -1
        wanted_data = []
        for row in csvreader:
            row_id += 1
            if row_id == 0 and not include_header:
                continue
            line = []
            col_id = -1
            is_wanted_row = False
            if city_name is None:
                is_wanted_row = True
            for raw_col in row:
                col_id += 1
                col = raw_col.replace('"', '')
                line.append( col )
                if col_id == 0 and city_name is not None:
                    if not exact_match and city_name.lower() in col.lower():
                        is_wanted_row = True
                    elif exact_match and city_name.lower() == col.lower():
                        is_wanted_row = True
            if is_wanted_row:
                if row_id > 0:
                    line.insert(0, "{}".format(row_id))
                else:
                    line.insert(0, "")
                wanted_data.append(line)
    return wanted_data

@app.route('/data', methods=['GET'])
def query():
    city_name = request.args.get('city_name')
    if city_name is not None:
        city_name = city_name.replace('"', '')
    wanted_data = fetch_data(city_name = city_name, include_header = True)
    table_content = ""
    for row in wanted_data:
        line_str = ""
        for col in row:
            line_str += "<td>" + col + "</td>"
        table_content += "<tr>" + line_str + "</tr>"
    page = "<html><title>Tutorial of CSE6332 - Part2</title><body>"
    page += "<table>" + table_content + "</table>"
    page += "</body></html>"
    return page
@app.route("/", methods=['GET'])
def index():
    message = "Congratulations, it's a web app!"
    return render_template(
            'app.html',
            message=message,
    )



def append_or_update_data(req):
    city_name = req['city_name']
    lat = req['lat']
    lng = req['lng']
    country = req['country']
    state = req['state']
    population = req['population']

    if city_name is None:
        return False

    input_line = '"{}","{}","{}","{}","{}","{}"'.format(
        city_name, lat, lng, country, state, population,
    )

    existing_records = fetch_data(city_name = city_name, exact_match=True)
    if len(existing_records) == 0:
        with open('us-cities.csv', 'a') as f:
            f.write(input_line)
            f.close()
    else:
        all_records = fetch_data(include_header=True)
        lines = []
        for row in all_records:
            line_to_write = ""
            if row[1].lower() != city_name.lower():
                line_to_write = ",".join(['"{}"'.format(col) for col in row[1:]])
            else:
                line_to_write = input_line
            lines.append(line_to_write + "\n")
        with open('us-cities.csv', 'w') as f:
            f.writelines(lines)
            f.close()
    return True

@app.route('/data', methods=['PUT'])
def append_or_update():
    req = request.json

    if append_or_update_data(req):
        return "done"
    else:
        return "invalid input"

def delete_data(city_name):
    existing_records = fetch_data(city_name = city_name, exact_match=True)
    if len(existing_records) > 0:
        all_records = fetch_data(include_header=True)
        lines = []
        for row in all_records:
            if row[1].lower() != city_name.lower():
                line_to_write = ",".join(['"{}"'.format(col) for col in row[1:]])
                lines.append(line_to_write + "\n")
        with open('us-cities.csv', 'w') as f:
            f.writelines(lines)
            f.truncate()
            f.close()
        return True
    return False

@app.route('/data', methods=['DELETE'])
def delete():
    city_name = request.args.get('city_name')
    if city_name is not None:
        city_name = city_name.replace('"', '')
    else:
        return "invalid input"

    if delete_data(city_name):
        return "done"
    else:
        return "city does not exist"


# Load data files
reviews_df = pd.read_csv('amazon-reviews.csv')
cities_df = pd.read_csv('us-cities.csv')

# Merge dataframes on the key "city"
merged_df = pd.merge(reviews_df, cities_df, on='city', how='inner')

# Function to get popular words for a given city
def get_popular_words1(city_name, limit):
    if city_name:
        city_reviews = merged_df[merged_df['city'] == city_name]
    else:
        city_reviews = merged_df

    words_count = {}
    for review in city_reviews['review']:
        words = review.split()
        for word in words:
            # Consider only alphanumeric words
            if word.isalnum():
                words_count[word.lower()] = words_count.get(word.lower(), 0) + 1

    sorted_words = sorted(words_count.items(), key=lambda x: x[1], reverse=True)[:limit]

    result = [{"term": word, "popularity": count} for word, count in sorted_words]
    return result

# RESTful API endpoint
@app.route('/popular_words1', methods=['GET'])
def popular_words1():
    city_name = request.args.get('city', None)
    limit = int(request.args.get('limit', 10))

    popular_words_result = get_popular_words1(city_name, limit)

    return jsonify(popular_words_result)


# Function to get popular words for a given city
def get_popular_words(city_name, limit):
    if city_name:
        city_reviews = merged_df[merged_df['city'] == city_name]
    else:
        city_reviews = merged_df

    words_population = {}
    for _, row in city_reviews.iterrows():
        words = row['review'].split()
        for word in words:
            # Consider only alphanumeric words
            if word.isalnum():
                words_population[word.lower()] = words_population.get(word.lower(), 0) + row['population']

    sorted_words = sorted(words_population.items(), key=lambda x: x[1], reverse=True)[:limit]

    result = [{"term": word, "popularity": count} for word, count in sorted_words]
    return result

# RESTful API endpoint
@app.route('/popular_words', methods=['GET'])
def popular_words():
    city_name = request.args.get('city', None)
    limit = int(request.args.get('limit', 10))

    popular_words_result = get_popular_words(city_name, limit)

    return jsonify(popular_words_result)

# RESTful API endpoint for word substitution
@app.route('/substitute_words', methods=['POST'])
def substitute_words():
    request_data = request.get_json()

    if 'words' not in request_data or 'substitute' not in request_data:
        return jsonify({"error": "Invalid request format"}), 400

    word_to_substitute = request_data['words'].lower()
    substitute_word = request_data['substitute']

    affected_reviews_count = 0

    for index, row in merged_df.iterrows():
        review = row['review'].lower()
        updated_review = review.replace(word_to_substitute, substitute_word)

        if updated_review != review:
            merged_df.at[index, 'review'] = updated_review
            affected_reviews_count += 1

    return jsonify({"affected_reviews": affected_reviews_count})



if __name__ == '__main__':
    app.run(debug=True)





