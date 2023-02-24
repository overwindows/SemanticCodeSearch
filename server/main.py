#!/usr/local/bin/python3
import json
import argparse
from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from server.code_search import CodeSearch

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
'''
generator = None
models = None
max_positions = None
align_dict = None
'''


@app.route("/search", methods=['GET'])
@cross_origin()
def search():
    query = request.args.get("query")
    print(query)
    json_res = []
    # for lang in ['python', 'go', 'javascript', 'java', 'php', 'ruby']:
    for lang in args.lang:
        sample_json = CODESERACH.search(query, language=lang)
        json_res.extend(sample_json)
        # if lang == 'python':
        #     cpp_sample_json = sample_json[:]
        #     for ix in range(len(cpp_sample_json)):
        #         cpp_sample_json[ix]['categories'] = ['cpp*']
        #         cpp_sample_json[ix]['description'] = CODETRANS.translate(cpp_sample_json[ix]['description'])
        #     json_res.extend(cpp_sample_json)
    return jsonify(json_res)


argparse = argparse.ArgumentParser()
argparse.add_argument('--model_path', type=str,
                      default='/root/neuralbow_hybrid-2020-07-05-13-43-57_model_best.pkl.gz')
argparse.add_argument('--data_path', type=str, default='/root/')
argparse.add_argument('--port', type=int, default=8000)
argparse.add_argument('--host', type=str, default='0.0.0.0')
argparse.add_argument('--lang', nargs='+', default=['python','go','javascript','java','php','ruby'])

args = argparse.parse_args()

if __name__ == "__main__":
    print('server is running on port: {}'.format(args.port))
    print('server is running on host: {}'.format(args.host))
    print('server is running on lang: {}'.format(args.lang))
    CODESERACH = CodeSearch(args.model_path)
    CODESERACH.load_model(args.data_path, langs_list=args.lang)
    print('loading completed.')
    try:
        app.run(host='0.0.0.0', debug=False, use_reloader=False, port=8000)
    except KeyboardInterrupt as e:
        print("[STOP]", e)
