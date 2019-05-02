from env.importing import hmean
from env.project_variables import TASKS_PARAMETER
from io_.info_print import printing


def get_perf_rate(metric, score_dic, n_tokens_dic, agg_func, task="normalize", verbose=1):
    """
    provides metric : the confusion matrix standart rates for the given task
    :param metric:
    :param score_dic: two level dictionay : first level for agg_func second
    for prediciton class based on CLASS_PER_TASK and task
    :param agg_func:
    :return: rate, denumerator of the rate (if means like f1 : returns all )
    """
    if metric in ["recall", "f1", "accuracy"]:
        positive_obs = n_tokens_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][1]]
        recall = score_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][1]] / positive_obs if positive_obs>0 else None
        if positive_obs==0:
            printing("WARNING : no positive observation were seen ", verbose=verbose, verbose_level=1)
        if metric == "recall":
            return recall, positive_obs
    if metric in ["precision", "f1", "accuracy"]:
        positive_prediction = n_tokens_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][0]] - score_dic[agg_func][
            TASKS_PARAMETER[task]["predicted_classes"][0]] + score_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][1]]
        precision = score_dic[agg_func][
                        TASKS_PARAMETER[task]["predicted_classes"][1]] / positive_prediction if positive_prediction > 0 else None
        if metric == "precision":
            return precision, \
                   positive_prediction
    if metric in ["tnr", "accuracy", 'f1']:
        negative_obs = n_tokens_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][0]]
        if metric == "tnr":
            return score_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][0]] / negative_obs, \
                   negative_obs
    if metric == "f1":
        if recall is not None and precision is not None and recall>0 and precision>0:
            return hmean([recall, precision]), negative_obs + positive_obs
        else:
            return None, negative_obs + positive_obs

    if metric in ["npvr"]:
        negative_prediction = n_tokens_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][1]] - score_dic[agg_func][
            TASKS_PARAMETER[task]["predicted_classes"][1]] + score_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][0]]
        return score_dic[agg_func][
                   TASKS_PARAMETER[task]["predicted_classes"][0]] / negative_prediction if negative_prediction > 0 else None, \
               negative_prediction
    if metric == "accuracy":
        accuracy = (score_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][0]] +
                    score_dic[agg_func][TASKS_PARAMETER[task]["predicted_classes"][1]]) / (positive_obs + negative_obs)
        return accuracy, positive_obs + negative_obs

    raise(Exception("metric {} not supported".format(metric)))
