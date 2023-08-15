from flask import Flask, request
import csv

app = Flask(__name__)

CSV_FILE = 'ad_data.csv'

@app.route('/ad_data', methods=['POST'])
def ad_data():
    data = request.get_json()
    items = data['data']
    name = data['name']

    with open('csv/{}.csv'.format(name), mode='a', newline='') as csv_file:
        fieldnames = ['network_name', 'latency', 'state', 'error_message', 'network_message', 'result_latency']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if csv_file.tell() == 0:
            writer.writeheader()

        writer.writerows(items)

    return 'OK'

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 5000
    app.run(host=HOST, port=PORT)
