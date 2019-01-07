from training.train import train
from io_.info_print import printing
import os
from evaluate.evaluate_epoch import evaluate
from env.project_variables import PROJECT_PATH, TRAINING, DEV, TEST, CHECKPOINT_DIR, DEMO, DEMO2, REPO_DATASET, LIU
from uuid import uuid4



def train_eval(train_path, dev_path, model_id_pref, n_epochs=11,
               warmup=False, args={},use_gpu=None,freq_checkpointing=1,
               verbose=0):



    hidden_size_encoder = args.get("hidden_size_encoder", 10)
    output_dim = args.get("output_dim",10)
    char_embedding_dim = args.get("char_embedding_dim",10)
    hidden_size_sent_encoder = args.get("hidden_size_sent_encoder", 10)
    hidden_size_decoder = args.get("hidden_size_decoder", 10)
    batch_size = args.get("batch_size", 2)
    dropout_sent_encoder, dropout_word_encoder, dropout_word_decoder = args.get("dropout_sent_encoder",0), \
    args.get("dropout_word_encoder",0), args.get("dropout_word_decoder",0)
    n_layers_word_encoder = args.get("n_layers_word_encoder",1)
    dir_sent_encoder = args.get("dir_sent_encoder", 1)

    n_epochs = 1 if warmup else n_epochs

    if warmup:
        printing("Warm up : running 1 epoch ", verbose=verbose, verbose_level=0)
    printing("START TRAINING ", verbose_level=0, verbose=verbose)
    model_full_name = train(train_path, dev_path, n_epochs=n_epochs, normalization=True,
                            batch_size=batch_size, model_specific_dictionary=True,
                            dict_path=None, model_dir=None, add_start_char=1,
                            add_end_char=1, use_gpu=use_gpu, dir_sent_encoder=dir_sent_encoder,
                            dropout_sent_encoder=dropout_sent_encoder, dropout_word_encoder=dropout_word_encoder, dropout_word_decoder=dropout_word_decoder,
                            label_train=REPO_DATASET[train_path], label_dev=REPO_DATASET[dev_path],
                            freq_checkpointing=freq_checkpointing, reload=False, model_id_pref=model_id_pref,
                            hidden_size_encoder=hidden_size_encoder, output_dim=output_dim, char_embedding_dim=char_embedding_dim,
                            hidden_size_sent_encoder=hidden_size_sent_encoder, hidden_size_decoder=hidden_size_decoder,
                            n_layers_word_encoder=n_layers_word_encoder,
                            print_raw=False, debug=False,
                            checkpointing=True)

    model_dir = os.path.join(CHECKPOINT_DIR, model_full_name+"-folder")
    dict_path = os.path.join(CHECKPOINT_DIR, model_full_name+"-folder", "dictionaries")
    printing("START EVALUATION ", verbose_level=0, verbose=verbose)
    for eval_data in [dev_path, train_path] :
            eval_label = REPO_DATASET[eval_data]
            evaluate(model_full_name=model_full_name, data_path=eval_data,
                     dict_path=dict_path,use_gpu=use_gpu,
                     label_report=eval_label,
                     normalization=True,print_raw=False,
                     model_specific_dictionary=True,
                     batch_size=batch_size,
                     dir_report=model_dir, verbose=1)

if __name__ == "__main__":

      train_path = LIU
      dev_path = DEV
      params = []

      model_id_pref_list = ["50batch-bi-dir-no_dropout", "50b-unidir-no_dropout"]

      if False:
        params.append({"hidden_size_encoder": 50, "output_dim": 100, "char_embedding_dim": 100,
                       "dropout_sent_encoder": 0., "dropout_word_encoder": 0., "dropout_word_decoder": 0.,
                       "n_layers_word_encoder": 1, "dir_sent_encoder": 2,
                       "hidden_size_sent_encoder": 50, "hidden_size_decoder": 100, "batch_size": 2})
        
        params.append({"hidden_size_encoder": 50, "output_dim": 100, "char_embedding_dim": 100,
                       "dropout_sent_encoder": 0., "dropout_word_encoder": 0., "dropout_word_decoder": 0.,
                       "n_layers_word_encoder": 1, "dir_sent_encoder": 2,
                       "hidden_size_sent_encoder": 50, "hidden_size_decoder": 100, "batch_size": 10})
        
      params.append({"hidden_size_encoder": 50, "output_dim": 100, "char_embedding_dim": 100,
                     "dropout_sent_encoder": 0., "dropout_word_encoder": 0., "dropout_word_decoder": 0.,
                     "n_layers_word_encoder": 1, "dir_sent_encoder": 2,
                     "hidden_size_sent_encoder": 50, "hidden_size_decoder": 100, "batch_size": 50})

      params.append({"hidden_size_encoder": 50, "output_dim": 100, "char_embedding_dim": 100,
                     "dropout_sent_encoder": 0., "dropout_word_encoder": 0., "dropout_word_decoder": 0.,
                     "n_layers_word_encoder": 1, "dir_sent_encoder": 1,
                     "hidden_size_sent_encoder": 50, "hidden_size_decoder": 100, "batch_size": 50})
      i = 0
      RUN_ID = str(uuid4())[0:4]

      for param, model_id_pref in zip(params, model_id_pref_list):
          i += 1
          param["batch_size"] = 2
          model_id_pref = "TEST"
          printing("Adding RUN_ID {} as prefix".format(RUN_ID), verbose=0, verbose_level=0)
          epochs = 1
          #param["batch_size"] = 50
          train_path, dev_path = DEMO2, DEMO2
          model_id_pref = RUN_ID + "-" + model_id_pref + "-model_"+str(i)
          print("STARTING MODEL {} with param {} ".format(model_id_pref, param))
          train_eval(train_path, dev_path, model_id_pref, warmup=False, args=param, use_gpu=None, n_epochs=epochs)
          print("DONE MODEL {} with param {} ".format(model_id_pref, param))

# CCL want to have a specific seed : when work --> reproduce with several seed