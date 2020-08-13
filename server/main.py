#!/usr/local/bin/python3

from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# patchgen = PatchGen()
# sp = spm.SentencePieceProcessor()
'''
generator = None
models = None
max_positions = None
align_dict = None
'''
@app.route("/search", methods=['GET'])
@cross_origin()
def search():
    sample_json = json.load(open('react-code-search/public/apps.json', 'r'))
    print(sample_json)
    return jsonify(sample_json)

# @app.route("/translate", methods=['POST'])
# @cross_origin()
# def get_gen():
#     data = request.get_json()
#     #print(data)
#     str_code = None
#     result = None
#     if 'text' not in data or len(data['text']) == 0 or 'model' not in data:
#         abort(400)
#     else:
#         text = data['text']
#         model = data['model']
#         #print(text)
#         if args.spm:
#             str_code = ' '.join(sp.EncodeAsPieces(normalizeSnippet(text)))
#         else:
#             str_code = normalizeSnippet(text, tokenize=True)
#         #print(str_code, sp.DecodePieces(str_code.split()))
#         ret = patchgen.generate_patch(str_code)
#         #print(ret)
#         if args.spm:
#             result = ''.join(sp.DecodePieces(ret.split()))
#         else:
#             result = decodeSnippet(ret)
#         '''
#         result = generate_text(
#             model_type='gpt2',
#             length=100,
#             prompt=text,
#             model_name_or_path=model
#         )
#         '''
#         return jsonify({'result': result})


if __name__ == "__main__":
    #parser = options.get_generation_parser(interactive=True)
    #args = options.parse_args_and_arch(parser)
    #patchgen.load_model(args)
    #if args.spm:
        #sp.Load('sentencepiece.bpe.model')
    #    sp.load(args.spm)
    app.run(host='0.0.0.0', debug=True)
