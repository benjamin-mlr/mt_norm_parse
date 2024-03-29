from env.importing import *
from toolbox.grid_tool import is_arg_available

from env.project_variables import PROJECT_PATH
from toolbox.grid_tool import grid_param_label_generate, get_experimented_tasks
from io_.info_print import printing
from env.project_variables import PROJECT_PATH, TRAINING,LIU_TRAIN, DEMO_SENT, CP_WR_PASTE_TEST_269, \
    LIU_DEV, DEV, DIR_TWEET_W2V, TEST, DIR_TWEET_W2V, CHECKPOINT_DIR, DEMO, DEMO2, CP_PASTE_WR_TRAIN, \
    CP_WR_PASTE_DEV, CP_WR_PASTE_TEST, CP_PASTE_DEV, CP_PASTE_TRAIN, CP_PASTE_TEST, EWT_DEV, EWT_TEST, \
    LIU_DEV_SENT, LIU_TRAIN_SENT, DEV_SENT, TEST_SENT, DEMO_SENT, TRAINING_DEMO, EN_LINES_EWT_TRAIN, EN_LINES_DEV, EN_LINES_EWT_TRAIN, \
    MTNT_TOK_TRAIN, MTNT_TOK_DEV, MTNT_EN_FR_TRAIN, MTNT_EN_FR_DEV, MTNT_EN_FR_TEST, LIST_ARGS, NONE_ARGS, BOOL_ARGS, RUN_SCRIPTS_DIR, GPU_AVAILABLE_DEFAULT_LS, DIC_ARGS, WARMUP_N_EPOCHS
from toolbox.git_related import get_commit_id
from tracking.reporting_google_sheet import append_reporting_sheet

params_dozat = {"hidden_size_encoder": 200, "output_dim": 100, "char_embedding_dim": 100,
                "dropout_sent_encoder": 0.5, "drop_out_word_encoder": 0.5, "dropout_word_decoder": 0.3,
                "drop_out_word_encoder_out": 0.5, "drop_out_sent_encoder_out": 0.0,
                "drop_out_char_embedding_decoder": 0.1, "dropout_bridge": 0.5,
                "n_layers_word_encoder": 1, "dir_sent_encoder": 2, "word_recurrent_cell_decoder": "LSTM",
                "word_recurrent_cell_encoder": "LSTM",
                "hidden_size_sent_encoder": 200, "hidden_size_decoder": 100, "batch_size": 500}


def script_generation(grid_label, init_param, warmup, dir_grid, environment, dir_log, epochs,
                      train_path, dev_path, test_paths, overall_report_dir, overall_label,
                      stable_decoding_state_ls, word_decoding_ls, batch_size_ls,
                      word_embed_ls, dir_sent_encoder_ls, lr_ls, word_embed_init_ls,
                      teacher_force_ls, proportion_pred_train_ls, shared_context_ls,
                      word_embedding_projected_dim_ls,
                      word_recurrent_cell_encoder_ls, dropout_word_encoder_cell_ls,
                      tasks_ls, char_src_attention_ls, mode_word_encoding_ls, char_level_embedding_projection_dim_ls,
                      n_layers_sent_cell_ls, unrolling_word_ls,attention_tagging_ls, n_layers_word_encoder_ls,
                      multi_task_loss_ponderation_ls, dir_word_encoder_ls,
                      dropout_input_ls,
                      scale_ls, checkpointing_metric_ls=None, pos_specific_path=None, gpu_mode="random", description_comment="",
                      gpus_ls=None, write_to_dir=None,test_before_run=False, scoring_func=None,
                      initialize_bpe_layer_ls=None, gold_error_detection_ls=None, heuristic_ls_ls=None,
                      freeze_layer_prefix_ls_ls=None,
                      freeze_parameters_ls=None,
                      bert_model_ls=None, dropout_classifier_ls=None, fine_tuning_strategy_ls=None, dropout_input_bpe_ls=None, dropout_bert_ls=None,
                      masking_strategy_ls=None,checkpoint_dir_ls=None, norm_2_noise_training_ls=None, aggregating_bert_layer_mode_ls=None,bert_module_ls=None,
                      layer_wise_attention_ls=None,tokenize_and_bpe_ls=None, append_n_mask_ls=None,
                      py_script="train_evaluate_run"):
    """

    NB train_ls, dev_ls, test_ls and tasks are handled differently than all the others
    :return:
    """
    printing("GRID RUN : INFO : we are iterating on zip(train_ls, dev_ls, test_ls, tasks ) a grid of all other parameters ls ", verbose_level=1, verbose=1)
    test_paths = [[",".join(path) for path in test_path_grid] for test_path_grid in test_paths]
    if write_to_dir is not None:
        script_dir = os.path.join(write_to_dir, "{}-run.sh".format(overall_label))
    warmup_desc = "warmup" if warmup else ""
    if test_before_run:
        warmup_desc += " test_before_run"
    params, labels, default_all, analysed, fixed = grid_param_label_generate(
                                                                            init_param, py_script=py_script,
                                                                            train_ls=train_path, dev_ls=dev_path, test_ls=test_paths, checkpointing_metric_ls=checkpointing_metric_ls,
                                                                            scoring_func=scoring_func,
                                                                            grid_label=grid_label,
                                                                            stable_decoding_state_ls=stable_decoding_state_ls,
                                                                            word_decoding_ls=word_decoding_ls,
                                                                            batch_size_ls=batch_size_ls,
                                                                            word_embed_ls=word_embed_ls,
                                                                            dir_sent_encoder_ls=dir_sent_encoder_ls, lr_ls=lr_ls,
                                                                            word_embed_init_ls=word_embed_init_ls,
                                                                            teacher_force_ls=teacher_force_ls,
                                                                            proportion_pred_train_ls=proportion_pred_train_ls,
                                                                            shared_context_ls=shared_context_ls,
                                                                            word_recurrent_cell_encoder_ls=word_recurrent_cell_encoder_ls,
                                                                            dropout_word_encoder_cell_ls=dropout_word_encoder_cell_ls,
                                                                            word_embedding_projected_dim_ls=word_embedding_projected_dim_ls,
                                                                            tasks_ls=tasks_ls,
                                                                            attention_tagging_ls=attention_tagging_ls,
                                                                            char_src_attention_ls=char_src_attention_ls,
                                                                            n_layers_sent_cell_ls=n_layers_sent_cell_ls,
                                                                            dir_word_encoder_ls=dir_word_encoder_ls,
                                                                            multi_task_loss_ponderation_ls=multi_task_loss_ponderation_ls,
                                                                            mode_word_encoding_ls=mode_word_encoding_ls,
                                                                            char_level_embedding_projection_dim_ls=char_level_embedding_projection_dim_ls,
                                                                            unrolling_word_ls=unrolling_word_ls,
                                                                            n_layers_word_encoder_ls=n_layers_word_encoder_ls, dropout_input_ls=dropout_input_ls,
                                                                            scale_ls=scale_ls, gpu_mode=gpu_mode, gpus_ls=gpus_ls,
                                                                            initialize_bpe_layer_ls=initialize_bpe_layer_ls,
                                                                            freeze_layer_prefix_ls_ls=freeze_layer_prefix_ls_ls,
                                                                            freeze_parameters_ls=freeze_parameters_ls,
                                                                            bert_model_ls=bert_model_ls,
                                                                            dropout_classifier_ls=dropout_classifier_ls,
                                                                            fine_tuning_strategy_ls=fine_tuning_strategy_ls,
                                                                            gold_error_detection_ls=gold_error_detection_ls, heuristic_ls_ls=heuristic_ls_ls,
                                                                            dropout_input_bpe_ls=dropout_input_bpe_ls, dropout_bert_ls=dropout_bert_ls,
                                                                            masking_strategy_ls=masking_strategy_ls, checkpoint_dir_ls=checkpoint_dir_ls,
                                                                            norm_2_noise_training_ls=norm_2_noise_training_ls, aggregating_bert_layer_mode_ls=aggregating_bert_layer_mode_ls,
                                                                            append_n_mask_ls=append_n_mask_ls,
                                                                            bert_module_ls=bert_module_ls, layer_wise_attention_ls=layer_wise_attention_ls,tokenize_and_bpe_ls=tokenize_and_bpe_ls,
                                                                            )
    if gpu_mode == "random":
        if gpus_ls is None:
            gpus_ls = GPU_AVAILABLE_DEFAULT_LS
    if gpu_mode == "fixed":
        if gpus_ls is None:
            gpus_ls = ["0"]
    mode_run = "dist"
    description = "{} - {} ({}) : Analysing : {} with regard to {} fixed".format(len(params) if not warmup else str(1)+"_WARMUP",
                                                                                 description_comment, mode_run, analysed, fixed)
    try:
        row, col = append_reporting_sheet(git_id=get_commit_id(), tasks=get_experimented_tasks(params)+"-{}.py".format(py_script),
                                          rioc_job=os.environ.get("OAR_JOB_ID", "local"+grid_label), description=description,
                                          log_dir=dir_log, target_dir=dir_grid + " | " + os.path.join(CHECKPOINT_DIR,
                                                                                                  "{}*".format(grid_label)),
                                          env=environment, status="running {}".format(warmup_desc),
                                          verbose=1)
    except Exception as e:
        printing("GOOGLE SHEET CONNECTION FAILED {}", var=[e], verbose=1, verbose_level=1)
        row = None

    for ind, (param, model_id_pref) in enumerate(zip(params, labels)):
        script = "CUDA_VISIBLE_DEVICES={} {} {}".format(ind % len(gpus_ls), os.environ.get("PYTHON_CONDA", "python"), os.path.join(PROJECT_PATH, "{}.py".format(py_script)))
        for arg, val in param.items():
            # args in NONE ARGS ARE NOT ADDED TO THE SCRIPT MAKER (they will be handle by default behavior later in the code)
            if not is_arg_available(script=py_script, arg=arg):
                continue
            #pdb.set_trace()
            if val is None:
                # WE SKIP NONE VALUE : (None --> default ArgumentParser value for the given argument)
                continue
            if arg in BOOL_ARGS:
                val = int(val)
            if arg in DIC_ARGS and not isinstance(val, str) and not isinstance(val, float):
                to_write = ""
                for key, value_arg in val.items():
                    to_write +="{}={},".format(key, value_arg)
                script += " --{} {}".format(arg, to_write)
            elif arg in DIC_ARGS:# in the case of mulitask there is this case also
                script += " --{} {}".format(arg, val)
            if arg not in LIST_ARGS and arg not in DIC_ARGS:
                script += " --{} {}".format(arg, val)
            elif arg in LIST_ARGS:
                script += " --{} {}".format(arg, " ".join(val))

            #script += " --{} {}".format("train_path", " ".join())
            #script += " --{} {}".format("dev_path", " ".join(dev_path))
            #if test_paths is not None:
            #    script += " --{} {}".format("test_path", " ".join(test_paths))
        if pos_specific_path is not None:
            script += " --{} {}".format("pos_specific_path", pos_specific_path)
        script += " --{} {}".format("overall_label", overall_label)
        script += " --{} {}".format("model_id_pref", model_id_pref)
        script += " --{} {}".format("epochs", epochs if not (warmup or test_before_run) else WARMUP_N_EPOCHS)
        script += " --{} {}".format("overall_report_dir", overall_report_dir)
        #print(script)
        if write_to_dir is not None:
            if ind == 0:
                assert not os.path.isfile(script_dir), "ERROR script_dir already exists can't do that"
                mode = "w"
            else:
                mode = "a"
            with open(script_dir+"-"+str(ind)+".sh", "w") as file:
                file.write(script)
            with open(script_dir, mode) as file:
                file.write("sh "+script_dir+"-"+str(ind)+".sh"+"\n")
        if warmup:
            break
    if write_to_dir is not None:
        printing("WRITTEN to {}", var=[script_dir], verbose_level=1, verbose=1)
    return script_dir, row


if __name__ == "__main__":

    from uuid import uuid4

    test_before_run = False
    epochs = 1
    LABEL_GRID = str(uuid4())[0:5]

    script_generation(py_script="train_evaluate_bert_normalizer",
                      init_param=params_dozat,
                      grid_label=LABEL_GRID,
                      word_recurrent_cell_encoder_ls=["LSTM"],
                      dropout_word_encoder_cell_ls=[0.1],
                      stable_decoding_state_ls=[0],
                      word_decoding_ls=[0],
                      batch_size_ls=[50, 80],
                      word_embed_ls=[0],
                      dir_sent_encoder_ls=[2], dir_word_encoder_ls=[2],
                      lr_ls=[0.001],
                      word_embed_init_ls=[None],#, DIR_FASTEXT_WIKI_NEWS_W2V, DIR_TWEET_W2V],
                      attention_tagging_ls=[1],
                      char_src_attention_ls=[1],
                      teacher_force_ls=[1],
                      proportion_pred_train_ls=[None],
                      shared_context_ls=["all"],
                      word_embedding_projected_dim_ls=[125],
                      char_level_embedding_projection_dim_ls=[125],
                      tasks_ls=[["normalize"]],
                      n_layers_sent_cell_ls=[2],
                      n_layers_word_encoder_ls=[1],
                      unrolling_word_ls=[1],
                      scoring_func="exact_match",
                      mode_word_encoding_ls=["sum"],
                      dropout_input_ls=[0.4],
                      multi_task_loss_ponderation_ls=[{"pos": 1, "normalize": 0, "norm_not_norm": 0, "edit_prediction":0},
                                                      # {"pos": 1, "normalize": 0, "norm_not_norm": 0.4, "edit_prediction":0},
                                                      # {"pos": 1, "normalize": 0, "norm_not_norm": 0.1 ,"edit_prediction":0},
                                                      # {"pos": 1, "normalize": 0, "norm_not_norm": 0.01, "edit_prediction":0.},
                                                     ],
                      scale_ls=[1],
                      # arguments that are specific to script generation
                      overall_report_dir="./", overall_label=LABEL_GRID,
                      train_path=[[DEV]], dev_path=[[TEST]], test_paths=[[[TEST, DEV]]],
                      warmup=test_before_run, test_before_run=test_before_run,
                      dir_grid="./", environment="local", dir_log="./",
                      epochs=epochs,
                      gpu_mode="random",
                      write_to_dir=RUN_SCRIPTS_DIR, description_comment="",
                      bert_model_ls=["cased"], initialize_bpe_layer_ls=[1], freeze_parameters_ls=[0],
                      freeze_layer_prefix_ls_ls=[None],
                      )


# default not used but could be

# HANDLE SPECIFIC BEHAVIOR
## Default behaviorn : ex None for path , behavior for test_paths as list
## bug quick fix

# to add : hardwares : gpu force true, cpu or gpu number
# write to script as list of scripts

# make sure : reports point to the correct directiory : summary and folders with same grid id and labels

# Task farm script that call this grid_script_generation , that call tracking : google sheet then should fit in the pipeline
# test on RIOC
# test on Neff
