#!/usr/local/bin/python3
import json

from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from server.code_search import CodeSearch 

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
CODESERACH = CodeSearch()

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
    for lang in ['python', 'go', 'javascript', 'java', 'php', 'ruby']:
        sample_json = CODESERACH.search(query, language=lang)
        json_res.extend(sample_json)
        # if lang == 'python':
        #     cpp_sample_json = sample_json[:]
        #     for ix in range(len(cpp_sample_json)):
        #         cpp_sample_json[ix]['categories'] = ['cpp*']
        #         cpp_sample_json[ix]['description'] = CODETRANS.translate(cpp_sample_json[ix]['description'])
        #     json_res.extend(cpp_sample_json)
    return jsonify(json_res)


@app.route("/translate", methods=['POST'])
@cross_origin()
def translate():
    data = request.get_json()
    # print(data)
    trans_code = CODETRANS.translate(data['code'])
    return jsonify({'cpp': trans_code})
    # str_code = None
    # result = None
    # if 'text' not in data or len(data['text']) == 0 or 'model' not in data:
    #     abort(400)
    # else:
    #     text = data['text']
    #     model = data['model']
    #     # print(text)
    #     if args.spm:
    #         str_code = ' '.join(sp.EncodeAsPieces(normalizeSnippet(text)))
    #     else:
    #         str_code = normalizeSnippet(text, tokenize=True)
    #     #print(str_code, sp.DecodePieces(str_code.split()))
    #     ret = patchgen.generate_patch(str_code)
    #     # print(ret)
    #     if args.spm:
    #         result = ''.join(sp.DecodePieces(ret.split()))
    #     else:
    #         result = decodeSnippet(ret)
    #     '''
    #     result = generate_text(
    #         model_type='gpt2',
    #         length=100,
    #         prompt=text,
    #         model_name_or_path=model
    #     )
    #     '''
    #     return jsonify({'result': result})


if __name__ == "__main__":
    #parser = options.get_generation_parser(interactive=True)
    #args = options.parse_args_and_arch(parser)
    CODESERACH.load_model()
    # CODETRANS.load_model()
    print('loading completed.')
    # codetrans.translate(python_code)
    # if args.spm:
    # sp.Load('sentencepiece.bpe.model')
    #    sp.load(args.spm)
    try:
        app.run(host='0.0.0.0', debug=False, use_reloader=False)
    except KeyboardInterrupt as e:
        print("[STOP]", e)
