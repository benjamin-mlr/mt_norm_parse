from model.sequence_prediction import greedy_decode_batch, decode_seq_str, decode_interacively
import pdb
from model.seq2seq import LexNormalizer, Generator
from io_.data_iterator import data_gen_conllu
from io_.dat import conllu_data
import os
import json
import sys
sys.path.insert(0, "/Users/benjaminmuller/Desktop/Work/INRIA/dev/experimental_pipe")

from reporting.write_to_performance_repo import report_template, write_dic


dict_path = "../dictionaries/"
train_path = "/Users/benjaminmuller/Desktop/Work/INRIA/dev/parsing/normpar/data/en-ud-train.conllu"
dev_pat = "/Users/benjaminmuller/Desktop/Work/INRIA/dev/parsing/normpar/data/owoputi.integrated"
test_path = "/Users/benjaminmuller/Desktop/Work/INRIA/dev/parsing/normpar/data/lexnorm.integrated"

normalization = False
add_start_char = 1

word_dictionary, char_dictionary, pos_dictionary,\
xpos_dictionary, type_dictionary = \
        conllu_data.create_dict(dict_path=dict_path,
                                train_path=test_path,
                                dev_path=test_path,
                                test_path=None,
                                add_start_char=add_start_char,
                                word_embed_dict={},
                                dry_run=False,
                                vocab_trim=True)

verbose = 2
_dir = os.path.dirname(os.path.realpath(__file__))
model = LexNormalizer(generator=Generator, load=True, model_full_name="auto_encoder_TEST_e528",#"6437",
                      dir_model=os.path.join(_dir, "..", "checkpoints"),
                      verbose=verbose)
batch_size = 2
nbatch = 1
verbose = 2
data_path = "/Users/benjaminmuller/Desktop/Work/INRIA/dev/parsing/normpar/data/lexnorm.integrated.demo2"
batchIter = data_gen_conllu(data_path, word_dictionary, char_dictionary, pos_dictionary, xpos_dictionary,
                            type_dictionary, batch_size=batch_size, nbatch=nbatch, add_start_char=add_start_char,
                            add_end_char=0,
                            normalization=normalization,
                            print_raw=True,  verbose=verbose)

V = model.arguments["hyperparameters"]["voc_size"]
model.eval()

batch_decoding = True

#loss = run_epoch(batchIter, model, LossCompute(model.generator, verbose=verbose),
#                     i_epoch=0, n_epochs=1,
#                     verbose=verbose,
#                     log_every_x_batch=100)
#print("LOSS", loss)
if batch_decoding:
    score_to_compute_ls = ["edit", "exact"]
    score_dic = greedy_decode_batch(char_dictionary=char_dictionary, verbose=2, gold_output=True,
                                    score_to_compute_ls=score_to_compute_ls,
                                    evaluation_metric="mean",
                                    batchIter=batchIter, model=model, batch_size=batch_size)
    # NB : each batch should have the same size !! same number of words : otherwise averaging is wrong
    try:
        for score in score_to_compute_ls:
            print("MODEL Normalization {} score is {} in average out of {} tokens on {} batches evaluation based on {} "
                  .format(score,score_dic[score]/score_dic[score+"total_tokens"], score_dic[score+"total_tokens"], nbatch, data_path ))
    except ZeroDivisionError as e:
        print("ERROR catched {} ".format(e))

    for score in score_to_compute_ls:
        report = report_template(metric_val=score, info_score_val="None", score_val=score_dic[score],
                                 model_full_name_val=model.model_full_name,
                                 report_path_val=os.path.dirname(os.path.realpath(__file__)),
                                 evaluation_script_val="normalization_"+score,
                                 model_args_dir=model.args_dir,
                                 data_val=test_path)
        dir_report = os.path.join("..", "checkpoints", model.model_full_name+"-folder",model.model_full_name+"-"+score+"-report.json")
        json.dump(report, open(dir_report, "w"))
        print(score, report)

        reporting = False
        if reporting:
            report_path = ""
            report_generation_script = "normalizer_edit"
            dir_performance_json = "/Users/benjaminmuller/Desktop/Work/INRIA/dev/experimental_pipe/model_repository/performancecopy.json"
            metric = "edit"
            write_dic(report_path, report_generation_script, dir_performance_json, metric, "None", model.model_full_name, test_path, 0)