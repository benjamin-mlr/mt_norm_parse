from env.importing import *

from io_.info_print import printing
from io_.dat.normalized_writer import write_conll
from model.sequence_prediction import decode_sequence, decode_word
from evaluate.normalization_errors import score_norm_not_norm
from evaluate.normalization_errors import score_ls_, correct_pred_counter
from env.project_variables import WRITING_DIR
from io_.dat.constants import PAD_ID_CHAR

# EPSILON for the test of edit distance
EPSILON = 0.000001
TEST_SCORING_IN_CODE = False



def _init_metric_report(score_to_compute_ls, mode_norm_score_ls):

    if score_to_compute_ls is not None:
        dic = {score+"-"+norm_mode: 0 for score in score_to_compute_ls for norm_mode in mode_norm_score_ls}
        dic.update({score + "-" + norm_mode + "-" + "n_sents": 0 for score in score_to_compute_ls for norm_mode in
                    mode_norm_score_ls})
        dic.update({score+"-"+norm_mode+"-"+"total_tokens": 0 for score in score_to_compute_ls for norm_mode in mode_norm_score_ls})
        dic.update({score+"-"+norm_mode+"-"+"mean_per_sent": 0 for score in score_to_compute_ls for norm_mode in mode_norm_score_ls})
        dic.update({score + "-" + norm_mode + "-" + "n_word_per_sent": 0 for score in score_to_compute_ls for norm_mode in mode_norm_score_ls})
        dic.update({token + "-norm_not_norm-" + type_ + "-count":0 for token in ["all","need_norm"] for type_ in ["pred", "gold"]})
        dic["all-norm_not_norm-pred_correct-count"] = 0
        dic["need_norm-norm_not_norm-pred_correct-count"] = 0
        return dic
    return None


def _init_metric_report_2():

    # TODO : factorize

    task = "normalize"
    formulas = {"recall-"+task+"": ("NEED_NORM-"+task+"-pred_correct-count", "NEED_NORM-"+task+"-gold-count"),
                "tnr-"+task+"": ("NORMED-"+task+"-pred_correct-count", "NORMED-"+task+"-gold-count"),
                "precision-"+task+"": ("NEED_NORM-"+task+"-pred_correct-count", "NEED_NORM-"+task+"-pred-count"),
                "npv-"+task+"": ("NORMED-"+task+"-pred_correct-count", "NORMED-"+task+"-pred-count"),
                "accuracy-"+task+"": ("all-"+task+"-pred_correct-count", "all-"+task+"-gold-count"),
                "accuracy-per_sent-"+task+"": ("all-"+task+"-pred_correct_per_sent-count", "all-"+task+"-n_sents"),
                "info-all-per_sent": ("all-"+task+"-n_word_per_sent-count", "all-"+task+"-n_sents"),
                "info-NORMED-per_sent": ("NORMED-"+task+"-n_word_per_sent-count", "NORMED-n_sents"),
                "recall-per_sent-"+task+"": ("NEED_NORM-"+task+"-pred_correct_per_sent-count", "NEED_NORM-n_sents"),
                "info-NEED_NORM-per_sent": ("NEED_NORM-"+task+"-n_word_per_sent-count", "NEED_NORM-"+task+"-n_sents"),
                "tnr-per_sent-"+task+"": ("NORMED-"+task+"-pred_correct_per_sent-count", "NORMED-"+task+"-n_sents"),
                "aa": ("n_sents", "n_sents"),
                "InV_accuracy-"+task+"": ("InV-"+task+"-pred_correct-count", "InV-"+task+"-gold-count"),
                "info-InV-per_sent": ("InV-"+task+"-n_word_per_sent-count", "InV-"+task+"-n_sents"),
                #"INV_accuracy-"+task+"": ("InV-"+task+"-pred_correct-count", "InV-"+task+"-gold-count"),
                "InV_accuracy-per_sent-"+task+"": ("InV-"+task+"-pred_correct_per_sent-count", "InV-"+task+"-n_sents"),
                #"OOV_accuracy-"+task+"": ("OOV-"+task+"-pred_correct-count", "OOV-"+task+"-gold-count"),
                "info-OOV-per_sent": ("OOV-"+task+"-n_word_per_sent-count", "OOV-"+task+"-n_sents"),
                "OOV_accuracy-"+task+"": ("OOV-"+task+"-pred_correct-count", "OOV-"+task+"-gold-count"),
                "OOV_accuracy-per_sent-"+task+"": ("OOV-"+task+"-pred_correct_per_sent-count", "OOV-"+task+"-n_sents")
                }

    formulas_2 = {
        "recall-norm_not_norm": ("need_norm-norm_not_norm-pred_correct-count", "need_norm-norm_not_norm-gold-count"),
        "precision-norm_not_norm": ("need_norm-norm_not_norm-pred_correct-count", "need_norm-norm_not_norm-pred-count"),
        "accuracy-norm_not_norm": ("all-norm_not_norm-pred_correct-count", "all-norm_not_norm-gold-count"),
        "IoU-pred-need_norm": (
        "need_norm-norm_not_normXnormalization-pred-count", "normed-norm_not_normUnormalization-pred-count"),
        "IoU-pred-normed": ("normed-norm_not_normXnormalization-pred-count", "need_norm-norm_not_normUnormalization-pred-count")
    }
    task = "pos"
    formula_pos = {
                #"recall-" + task + "": ("NEED_NORM-" + task + "-pred_correct-count", "NEED_NORM-" + task + "-gold-count"),
                #"recall-per_sent-" + task + "": ("NEED_NORM-" + task + "-pred_correct_per_sent-count", "NEED_NORM-"+task+"-n_sents"),
                #"tnr-" + task + "": ("NORMED-" + task + "-pred_correct-count", "NORMED-" + task + "-gold-count"),
                #"tnr-per_sent-" + task + "": ("NORMED-" + task + "-pred_correct_per_sent-count", "NORMED-"+task+"-n_sents"),
                "accuracy-"+task+"": ("all-"+task+"-pred_correct-count", "all-"+task+"-gold-count"),
                "accuracy-per_sent-"+task+"": ("all-"+task+"-pred_correct_per_sent-count", "all-"+task+"-n_sents"),
                "info-all-per_sent": ("all-"+task+"-n_word_per_sent-count", "all-"+task+"-n_sents"),
                "info-all_tokens-"+task+"": ("all-"+task+"-gold-count"),
                "info-"+task+"-n_sents": ("all-"+task+"-n_sents")
                }

    dic = OrderedDict()
    for a, (val, val2) in formulas.items():
        dic[val] = 0
        dic[val2] = 0
    for a, (val1, val12) in formulas_2.items():
        dic[val1] = 0
        dic[val12] = 0
    for a, tupl in formula_pos.items():
        if len(tupl) > 1:
            dic[tupl[0]] = 0
            dic[tupl[1]] = 0
        elif len(tupl) == 1:
            dic[tupl[0]] = 0

    dic["all-normalize-pred-count"] = 0
    return dic


def greedy_decode_batch(batchIter, model, char_dictionary, batch_size, task_simultaneous_eval, pad=PAD_ID_CHAR,
                        gold_output=False, score_to_compute_ls=None,
                        stat=None,
                        use_gpu=False,
                        compute_mean_score_per_sent=False,
                        mode_norm_score_ls=None,
                        label_data=None, eval_new=False,
                        scoring_func_sequence_pred="exact_match",
                        write_output=False, write_to="conll",
                        dir_normalized=None, dir_original=None,
                        verbose=0):
        "We decode batch by batch simultaneous ls of tasks at a time "
        score_dic = _init_metric_report(score_to_compute_ls, mode_norm_score_ls)

        counter_correct = _init_metric_report_2()
        total_count = {"src_word_count": 0,
                       "target_word_count": 0,
                       "pred_word_count": 0}
        if mode_norm_score_ls is None:
            mode_norm_score_ls = ["all"]

        assert len(set(mode_norm_score_ls) & set(["all", "NEED_NORM", "NORMED"])) > 0

        with torch.no_grad():
            i = -1
            while True:
                try:
                    batch = batchIter.__next__()
                    i += 1
                except StopIteration:
                    break
                src_seq = batch.input_seq
                src_len = batch.input_seq_len
                src_mask = batch.input_seq_mask
                target_gold = batch.output_seq if gold_output else None
                target_word_gold = batch.output_word if gold_output else None
                target_pos_gold = batch.pos if gold_output else None
                # do something with it : When do you stop decoding ?
                max_len = src_seq.size(-1)
                printing("WARNING : word max_len set to src_seq.size(-1) {} ", var=(max_len), verbose=verbose,
                         verbose_level=3)
                # decoding one batch
                src_text_ls = ""
                text_decoded_ls = ""
                gold_text_seq_ls = ""
                if "norm_not_norm" in task_simultaneous_eval:#model.arguments["hyperparameters"].get("tasks", ["normalize"]):
                    (text_decoded_ls, src_text_ls, gold_text_seq_ls, _), counts, _, \
                    (pred_norm, output_seq_n_hot, src_seq, target_seq_gold) = decode_word(model, src_seq, src_len,
                                                                                          input_word=batch.input_word,
                                                                                          mode="norm_not_norm"
                                                                                         )
                if "normalize" in task_simultaneous_eval:
                    if model.arguments["hyperparameters"]["decoder_arch"].get("char_decoding", True):
                        # TODO : should be able to merge word_decoding and char_decoding
                        assert not model.arguments["hyperparameters"]["decoder_arch"].get("word_decoding", False), \
                            "ERROR : only on type of decoding should be set (for now)"
                        (text_decoded_ls, src_text_ls, gold_text_seq_ls, _), counts, _, \
                        (pred_norm, output_seq_n_hot, src_seq, target_seq_gold) = decode_sequence(model=model,
                                                                                                  char_dictionary=char_dictionary,
                                                                                                  single_sequence=False,
                                                                                                  target_seq_gold=target_gold,
                                                                                                  use_gpu=use_gpu,
                                                                                                  max_len=max_len,
                                                                                                  src_seq=src_seq,
                                                                                                  src_mask=src_mask,
                                                                                                  src_len=src_len,
                                                                                                  input_word=batch.input_word,
                                                                                                  pad=pad,
                                                                                                  verbose=verbose)

                    if model.arguments["hyperparameters"]["decoder_arch"].get("word_decoding", False):
                        (text_decoded_ls, src_text_ls, gold_text_seq_ls, _), counts, _, \
                        (pred_norm, output_seq_n_hot, src_seq, target_seq_gold) = decode_word(model, src_seq, src_len,
                                                                                              input_word=batch.input_word,
                                                                                              mode="word",
                                                                                              target_word_gold=target_word_gold)
                if "pos" in task_simultaneous_eval:#model.arguments["hyperparameters"].get("tasks", ["normalize"]):
                    # decode pos
                    (pred_pos_ls, src_text_pos, gold_pos_seq_ls, _), counts_pos, _, \
                    (_, _, src_seq_pos, target_seq_gold_pos) = decode_word(model, src_seq, src_len,
                                                                           input_word=batch.input_word,
                                                                           mode="pos", target_pos_gold=target_pos_gold)
                else:
                    pred_pos_ls, src_text_pos, gold_pos_seq_ls = None, None, None

                if write_output:
                    if dir_normalized is None:
                        dir_normalized = os.path.join(WRITING_DIR, model.model_full_name +
                                                      "-{}-normalized.conll".format(label_data))
                        dir_original = os.path.join(WRITING_DIR, model.model_full_name +
                                                    "-{}-original.conll".format(label_data))

                    write_conll(format=write_to, dir_normalized=dir_normalized, dir_original=dir_original,
                                ind_batch=i*batch_size,
                                tasks=model.arguments["hyperparameters"].get("tasks", "normalize"),
                                text_decoded_ls=text_decoded_ls, src_text_ls=src_text_ls,
                                pred_pos_ls=pred_pos_ls, src_text_pos=src_text_pos,
                                new_file=i==0,
                                verbose=verbose)
                counts = None
                if counts is not None:
                    total_count["src_word_count"] += counts["src_word_count"]
                    total_count["pred_word_count"] += counts["pred_word_count"]
                printing("Source text {} ", var=[(src_text_ls)], verbose=verbose, verbose_level=5)
                printing("Prediction {} ", var=[(text_decoded_ls)], verbose=verbose, verbose_level=5)
                if gold_output:
                    if counts is not None:
                        total_count["target_word_count"] += counts["target_word_count"]

                    # we can score
                    printing("Gold {} ", var=[(gold_text_seq_ls)],
                             verbose=verbose, verbose_level=5)
                    # output exact score only
                    # sent mean not yet supported for npv and tnr, precision

                    counter_correct_batch = dict()
                    score_formulas = dict()
                    for task in task_simultaneous_eval:
                        if task == "edit_prediction":
                            continue
                        # TODO MULTITASK should factorize even more adding assertion on what we evaluate
                        if task == "pos":
                            target_seq_gold = gold_pos_seq_ls
                            ls_gold = gold_pos_seq_ls
                            ls_pred = pred_pos_ls
                            ls_original = src_text_pos
                            output_seq_n_hot = None
                            pred_norm_not_norm = None
                            in_vocab_ls = None
                            gold_norm_not_norm = None
                        elif task in ["normalize", "norm_not_norm"]:
                            ls_pred = text_decoded_ls
                            ls_gold = gold_text_seq_ls
                            output_seq_n_hot = output_seq_n_hot
                            src_seq = src_seq
                            in_vocab_ls = model.word_dictionary.inv_ls
                            target_seq_gold = target_seq_gold
                            pred_norm_not_norm = pred_norm
                            gold_norm_not_norm = batch.output_norm_not_norm
                            ls_original = src_text_ls
                        _counter_correct_batch, _score_formulas = correct_pred_counter(ls_pred=ls_pred,
                                                                                       ls_gold=ls_gold,
                                                                                       output_seq_n_hot=output_seq_n_hot,
                                                                                       src_seq=src_seq,
                                                                                       in_vocab_ls=in_vocab_ls,
                                                                                       target_seq_gold=target_seq_gold,
                                                                                       pred_norm_not_norm=pred_norm_not_norm,
                                                                                       task=task,
                                                                                       gold_norm_not_norm=gold_norm_not_norm,
                                                                                       scoring_func=scoring_func_sequence_pred,
                                                                                       ls_original=ls_original)
                        counter_correct_batch.update(_counter_correct_batch)
                        score_formulas.update(_score_formulas)

                    for key, val in counter_correct_batch.items():
                        try:
                            counter_correct[key] += val
                        except Exception as e:
                            print("key", key)
                            counter_correct[key] += 0
                            print(e)
                            print("EXXCEPTION WHEN updating counter_correct {} : val {} was therefore set to 0".format(key, val))
                    test_scoring = TEST_SCORING_IN_CODE
                    if test_scoring:
                        assert len(list((set(mode_norm_score_ls)& set(["NEED_NORM", "NORMED","all"])))) == 3, "ERROR : to perform test need all normalization mode "
                            #print("Scoring with mode {}".format(mode_norm_score))
                        for metric in score_to_compute_ls:
                            assert score_dic[metric + "-NEED_NORM-total_tokens"]+score_dic[metric + "-NORMED-total_tokens"] == score_dic[metric + "-all-total_tokens"], \
                                'ERROR all-total_tokens is {}  not equal to NEED NORMED {} +  NORMED {} '.format(score_dic[metric + "-all-total_tokens"], score_dic[metric + "-NEED_NORM-total_tokens"], score_dic[metric + "-NORMED-total_tokens"])
                            assert np.abs(score_dic[metric + "-NEED_NORM"]+score_dic[metric + "-NORMED"] - score_dic[metric + "-all"]) < EPSILON, "ERROR : correct NEED_NORM {} , NORMED {} and all {} ".format(score_dic[metric + "-NEED_NORM"], score_dic[metric + "-NORMED"], score_dic[metric + "-all"])
                            print("TEST PASSED")
            if gold_output:
                try:
                    assert total_count["src_word_count"] == total_count["target_word_count"], \
                        "ERROR src_word_count {} vs target_word_count {}".format(total_count["src_word_count"], total_count["target_word_count"])
                    assert total_count["src_word_count"] == total_count["pred_word_count"], \
                        "ERROR src_word_count {} vs pred_word_count {}".format(total_count["src_word_count"], total_count["pred_word_count"])
                    printing("Assertion passed : there are as many words in the source side,"
                             "the target side and"
                             "the predicted side : {} ".format(total_count["src_word_count"]), verbose_level=2,
                             verbose=verbose)
                except Exception as e:
                    print("Assertion failed count tokens")
                    print(e)

            if not eval_new:
                # i think we can remove it
                score_formulas = None

            return counter_correct, score_formulas

