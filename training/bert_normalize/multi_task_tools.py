from env.importing import OrderedDict, pdb
from io_.info_print import printing


def get_vocab_size_and_dictionary_per_task(tasks, pos_dictionary=None, type_dictionary=None, vocab_bert_wordpieces_len=None, task_parameters=None,verbose=1):
    # TODO : should be factorize with load dictionaries
    if pos_dictionary is None and type_dictionary is None:
        assert "pos" not in tasks and "parsing" not in tasks, \
            "ERROR : pos or parsing are in tasks but related dictionaries are None"
        printing("INFO : no dictionaries and voc_sizes needed", verbose=verbose, verbose_level=1)
        return None, None
    num_labels_per_task = OrderedDict()
    task_to_label_dictionary = OrderedDict()

    if "pos" in tasks:
        assert pos_dictionary is not None
        task_to_label_dictionary["pos-pos"] = pos_dictionary
        num_labels_per_task["pos-"+task_parameters["pos"]["label"][0]] = len(pos_dictionary.instance2index) + 1
    if "parsing" in tasks:
        assert type_dictionary is not None
        num_labels_per_task["parsing-types"] = len(type_dictionary.instance2index) + 1
        num_labels_per_task["parsing-heads"] = 0

        task_to_label_dictionary["parsing-types"] = type_dictionary
        task_to_label_dictionary["parsing-heads"] = "index"

    if "n_masks_mwe" in tasks:
        num_labels_per_task["n_masks_mwe-"+task_parameters["n_masks_mwe"]["label"][0]] = 3
        task_to_label_dictionary["n_masks_mwe-n_masks_mwe"] = "index"

    if "mwe_detection" in tasks:
        num_labels_per_task["mwe_detection-"+task_parameters["mwe_detection"]["label"][0]] = 2
        task_to_label_dictionary["mwe_detection-mwe_detection"] = "index"
    if "mwe_prediction" in tasks:
        assert vocab_bert_wordpieces_len is not None
        num_labels_per_task["mwe_prediction-"+task_parameters["mwe_prediction"]["label"][0]] = vocab_bert_wordpieces_len
        task_to_label_dictionary["mwe_prediction-mwe_prediction"] = "index"
    if "mlm" in tasks:
        assert vocab_bert_wordpieces_len is not None
        num_labels_per_task["mlm-" + task_parameters["mlm"]["label"][0]] = vocab_bert_wordpieces_len
        task_to_label_dictionary["mlm-"+task_parameters["mlm"]["label"][0]] = "index"

    return num_labels_per_task, task_to_label_dictionary
