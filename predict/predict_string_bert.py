from env.importing import *
from model.bert_tools_from_core_code.tokenization import BertTokenizer

from io_.info_print import printing
from io_.bert_iterators_tools.string_processing import get_indexes, from_bpe_token_to_str
from io_.bert_iterators_tools.alignement import realigne


def prediction_topk_to_string(predictions_topk, input_alignement_with_raw, topk, tokenizer,
                              null_token_index, null_str,tasks,
                              verbose=1):

    sentence_pred = from_bpe_token_to_str(predictions_topk, topk, null_str=null_str, null_token_index=null_token_index,
                                          tokenizer=tokenizer, pred_mode=True)
    sentence_pred_aligned = []

    for top in range(topk):
        realign_sent = realigne(sentence_pred[top], input_alignement_with_raw, tasks=tasks, null_str=null_str, remove_null_str=True,
                                mask_str="X")
        assert len(realign_sent) == 1, "ERROR : only batch len 1 accepted here (we are doing interaction)"
        printing("{} top-pred : bpe {}", var=[top, realign_sent],
                 verbose_level=2, verbose=verbose)
        realign_sent = " ".join(realign_sent[0])
        sentence_pred_aligned.append(realign_sent)
    return sentence_pred_aligned, sentence_pred


def bert_predict(input_string, bert_token_classification, tokenizer, verbose, null_str, null_token_index,
                 topk,  use_gpu, tasks):

    input_string = ["[CLS] " + input_string + " [SEP]"]

    input_tokens_tensor, input_segments_tensors, inp_bpe_tokenized, \
    input_alignement_with_raw, input_mask = get_indexes(input_string, tokenizer, verbose, use_gpu)
    token_type_ids = torch.zeros_like(input_tokens_tensor)

    # get prediction
    logits = bert_token_classification(input_tokens_tensor, token_type_ids, input_mask)
    predictions_topk = torch.argsort(logits, dim=-1, descending=True)[:, :, :topk]
    sentence_pred_aligned, sentence_pred = prediction_topk_to_string(predictions_topk, input_alignement_with_raw, topk, tokenizer,
                                                                     tasks=tasks,
                                                                     null_token_index=null_token_index, null_str=null_str)
    #get embedding
    embedding, _ = bert_token_classification.bert(input_tokens_tensor, token_type_ids, input_mask, output_all_encoded_layers = False)

    return {"pred": {"bpe":sentence_pred, "word":sentence_pred_aligned},
            "src": {"bpe":inp_bpe_tokenized, "word":input_string},
            "embedding": embedding.detach()}


def interact_bert(bert_token_classification,  tokenizer, null_token_index, null_str, tasks, topk=1, verbose=1,
                  print_input=True, use_gpu=False):

    printing("INFO : input_string should be white space tokenized", verbose=verbose, verbose_level=1)

    input_string = input("What would you like to normalize ? type STOP to stop ")
    if input_string == "STOP":
        print("ENDING interaction")
        return None, 0

    input_string = ["[CLS] " + input_string + " [SEP]"]

    input_tokens_tensor, input_segments_tensors, inp_bpe_tokenized, \
    input_alignement_with_raw, input_mask = get_indexes(input_string, tokenizer, verbose, use_gpu)
    token_type_ids = torch.zeros_like(input_tokens_tensor)
    if print_input:
        print("SRC : BPE ", inp_bpe_tokenized)
    logits = bert_token_classification(input_tokens_tensor, token_type_ids, input_mask)[0]["logits_task_1"] \
        if tasks[0] == "normalize" else None

    predictions_topk = torch.argsort(logits, dim=-1, descending=True)[:, :, :topk]

    sentence_pred_aligned, sentence_pred = prediction_topk_to_string(predictions_topk, input_alignement_with_raw,
                                                                     topk, tokenizer, tasks=tasks,
                                                                     null_token_index=null_token_index,
                                                                     null_str=null_str)

    return input_string, sentence_pred_aligned, sentence_pred

