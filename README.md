# Semantic Code Search
Semantic code search implementation using Tensorflow framework and the source code data from the [CodeSearchNet](https://wandb.ai/github/codesearchnet/benchmark/leaderboard) project. The model training pipeline was based on the implementation in [CodeSearchNet](https://github.com/github/CodeSearchNet) repository. Python, Java, Go, Php, Javascript, and Ruby programming language are supported.

## Model Description
BPE tokenizer is used to encode both code strings and query strings(docstrings are used as queries in training). Code strings are padded and encoded to the length of 200 tokens. Query strings are padded and encoded to the length of 30 tokens. Both code embedding size and query embedding size are 256. Token embeddings are masked and then an unweighted mean is performed to get a vector with 256 dimensions for code strings and query strings. Cosine similarity is calculated between the code representations and the query representations. Further details can be found on the [WANDB run](https://wandb.ai/github/codesearchnet/runs/zxe0vij0/overview)

## Model Structure
- Deep Structured Semantic Model
- Wide & Deep Learning

## Project Structure
Python package with scripts to prepare the data, train/test the model and predict.

## Data
We use the data from the CodeSearchNet project. The downloaded data is around 20GB. For more details, please follow this [link](https://github.com/github/CodeSearchNet/tree/master/resources)

## Training the model
To install the reqiured dependencies
```
pip3 install -r requirements.txt
```
### Preparing data
Data preparation step is seperated from the training step because of computing time and memory consumption.

### Training and evaluation
Start the training
```
python3 -m train --model neuralbow_v1
```
The model will be trained for each language. The evaluation metric is MRR for validation and test sets, however, the output of prediction will be evaluated by GitHub using nDCG.

### Checkpoints Download
- [Hybrid Model](https://api.wandb.ai/files/wuchen/SemanticCodeSearch/1fpfl6dq/neuralbow_hybrid-2020-07-05-13-43-57_model_best.pkl.gz)

### Query the trained model
Predict
```
python3 predict.py -r wuchen/SemanticCodeSearch/1fpfl6dq
```

## Online Semantic Code Search website
- Requirements: Flask <!--, ElasticSearch -->
- Import source code file
- Running the dev server
### Model Server
```
python3 -m server.main
```
### Web Front-End
```
cd react-code-search
npm install
npm start
```

### Citation
Please cite as:
```
@article{wu2022learning,
  title={Learning Deep Semantic Model for Code Search using CodeSearchNet Corpus},
  author={Wu, Chen and Yan, Ming},
  journal={arXiv preprint arXiv:2201.11313},
  year={2022}
}
```
<!-- Googl ScaNN -->
