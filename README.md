# Multitask learning 

Multitask learning framework for sequence prediction and sequence labelling 

## Environment setup 

This project works under two versions of pytorch : torch 0.4 and torch 1.0  

Therefore two possible conda env : 
- `conda env create -f lm.yml`  (1.0) (migh need to add missing, `pip install --upgrade oauth2client` !)

In `./env/project_variables.py` define BERT_MODELS_DIRECTORY as the location of the bert tar.gz and vocabulary file 

`mkdir BERT_MODELS_DIRECTORY`


## Downloading Bert Models 


`cd BERT_MODELS_DIRECTORY`

### Multilingual base cased model 

`curl -O "https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-multilingual-cased-vocab.txt"` <br>
`curl -O "https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-multilingual-cased.tar.gz"`

### English base cased model 

`curl -O  "https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-cased.tar.gz"` <br>
`curl -O "https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-cased-vocab.txt"`


## Data

Data should be in CoNLLU format https://universaldependencies.org/format.html

To download the all annotaded UD data 

`curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2899{/conll-2017-2018-blind-and-preprocessed-test-data.zip}`


## Training and evaluating 

```
python ./train_evaluate_bert_normalizer.py 
## Data
--train_path ./data/en-ud-train-demo.conll  # 
--dev_path ./data/en-ud-dev-demo.conll # 
--test_path ./data/en-ud-test-demo.conll  # 
## tasks 
--tasks pos ## as a space separated list of task among  ['normalize', 'pos', 'edit', 'norm_not_norm']
## tokenization 
--tokenize_and_bpe 0 #
## architecture
--bert_module mlm # 
--initialize_bpe_layer 1 #
--bert_model bert_base_multilingual_cased  # bert models cf. env/model_dir to see available models 
--aggregating_bert_layer_mode last ## 
--layer_wise_attention 0 ##
--append_n_mask 0
## optimization
--epochs 1 
--batch_size 2 #
--lr 5e-05 #
--freeze_parameters 0 #
--fine_tuning_strategy standart # 
## regularization 
--dropout_classifier 0.1 ## 
--dropout_input_bpe 0.0 ##
## dump path 
--overall_report_dir ./checkpoints/28d8d-B-summary #
--model_id_pref 28d8d-B-model_1 #
``` 

### Reporting details 

In ./checkpoint/bert/model_full_name folder :

Model dictionary, predictions, checkpoints, argument and performance report will be written in it 


