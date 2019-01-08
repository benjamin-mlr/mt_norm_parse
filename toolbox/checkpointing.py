from io_.info_print import printing
import torch


def checkpoint(loss_saved , loss, model, model_dir, epoch, epochs, info_checkpoint, saved_epoch,
               counter_no_decrease, verbose):
    if loss < loss_saved:
        saved_epoch = epoch
        loss_saved = loss
        printing('Checkpoint info : Loss decreased so saving model saved epoch is {} (counter_no_decrease set to 0)',var=saved_epoch, verbose=verbose, verbose_level=1)
        model.save(model_dir, model, info_checkpoint=info_checkpoint, suffix_name="Xep-outof{}ep".format(epochs), verbose=verbose)
        counter_no_decrease = 0
    else:
        # could add loading former model if loss suddenly pick
        #printing('Checkpoint info : Loss decreased so saving model', verbose=verbose, verbose_level=1)
        #model.load_state_dict(torch.load(checkpoint_dir))
        # TODO : load former checkpoint : and do change loss append IF error suddendly pick
        counter_no_decrease += 1
        printing("Checkpoint info: Loss did not decrease so keeping former model of epoch {} "
                 "counter_no_decrease is now {} ",
                 var=(saved_epoch, counter_no_decrease), verbose=verbose, verbose_level=1)

    return model, loss_saved , counter_no_decrease, saved_epoch


def update_curve_dic(score_to_compute_ls, mode_norm_ls, eval_data, scores, former_curve_scores):
    for mode in mode_norm_ls:
        for score in score_to_compute_ls:
            # adding count
            former_curve_scores[mode + "-" + eval_data] = scores[score + "-" + mode + "-total_tokens"]
            former_curve_scores[score + "-" + mode + "-" + eval_data].append(
                scores[score + "-" + mode] / scores[score + "-" + mode + "-total_tokens"])
    return former_curve_scores