import itertools

from env.importing import *
from io_.info_print import printing
from env.project_variables import TASKS_2_METRICS_STR, GPU_AVAILABLE_DEFAULT_LS, REPO_W2V, AVAILABLE_BERT_FINE_TUNING_STRATEGY, REPO_DATASET
from env.default_hyperparameters import *

sys.path.insert(0, os.environ.get("EXPERIENCE", ".."))
from meta_code.reporting_shared_variables import REPORT_FLAG_VARIABLES_EXPAND_STR, REPORT_FLAG_VARIABLES_ENRICH_STR, REPORT_FLAG_VARIABLES_ANALYSED_STR, REPORT_FLAG_VARIABLES_FIXED_STR

DEFAULT_BATCH_SIZE = 25
DEFAULT_SCALE = 2

#DEFAULT_AUX_NORM_NOT_NORM = False
GPU_MODE_SUPPORTED = ["random", "fixed", "CPU"]


def get_experimented_tasks(params):
  try:
    tasks_ls = ["+".join(param["tasks"]) for param in params]
    return str((set(tasks_ls)))
  except:
    return "?"


def get_gpu_id(gpu_mode, gpus_ls, verbose):
  if gpus_ls is None:
    if gpu_mode == "random":
      gpus_ls = GPU_AVAILABLE_DEFAULT_LS
      printing("ENV : switch to default gpu_ls {} cause mode is {}".format(gpus_ls, gpu_mode),
               verbose=verbose, verbose_level=1)
    if gpu_mode == "fixed":
      gpus_ls = ["0"]
      printing("ENV : switch to default gpu_ls {} cause mode is {}".format(gpus_ls, gpu_mode),
               verbose=verbose, verbose_level=1)
  if gpu_mode == "random":
    gpu = np.random.choice(gpus_ls,1)[0]
  elif gpu_mode == "fixed":
    assert len(gpus_ls) == 1, "ERROR : gpus_ls should be len 1 as gpu_mode fixed"
    gpu = gpus_ls[0]
  elif gpu_mode == "CPU":
    if gpu_mode == "CPU":
      printing("ENV : CPU mode (gpu_ls {} ignored) ", verbose=verbose, verbose_level=1)
    gpu = None
  return gpu


def is_arg_available(script, arg):

  assert script in AVAILABLE_TRAINING_EVAL_SCRIPT
  args_allowed = ARGS_AVAILABLE_PER_MODEL[script]

  if args_allowed[0] == 1:
    return 1
  else:
    return arg in args_allowed


def grid_param_label_generate(param,
                              train_ls, dev_ls, test_ls,
                              py_script="train_evaluate_run",
                              checkpointing_metric_ls=None,tasks_ls=None,
                              batch_size_ls=None, lr_ls=None, scale_ls =None,
                              shared_context_ls=None,
                              word_embed_init_ls=None, dir_word_encoder_ls=None, char_src_attention_ls=None, dir_sent_encoder_ls=None,
                              clipping_ls=None, unrolling_word_ls=None, teacher_force_ls=None,
                              word_decoding_ls=None,
                              dropout_word_encoder_cell_ls=None,
                              scoring_func=None,
                              stable_decoding_state_ls=None,word_recurrent_cell_encoder_ls=None,
                              word_embedding_projected_dim_ls=None, n_layers_sent_cell_ls=None, n_layers_word_encoder_ls=None,
                              word_embed_ls=None, char_level_embedding_projection_dim_ls=None, mode_word_encoding_ls=None,
                              dropout_input_ls=None,
                              proportion_pred_train_ls=None,  attention_tagging_ls=None, multi_task_loss_ponderation_ls=None,
                              grid_label="", gpu_mode="random", gpus_ls=None, printout_info_var=True,
                              initialize_bpe_layer_ls=None, freeze_parameters_ls=None, freeze_layer_prefix_ls_ls=None,
                              heuristic_ls_ls=None, gold_error_detection_ls=None,
                              bert_model_ls=None,dropout_classifier_ls=None, fine_tuning_strategy_ls=None,
                              dropout_input_bpe_ls=None, dropout_bert_ls=None,
                              masking_strategy_ls=None, checkpoint_dir_ls=None,norm_2_noise_training_ls=None,
                              aggregating_bert_layer_mode_ls=None, bert_module_ls=None,layer_wise_attention_ls=None,tokenize_and_bpe_ls=None,
                              append_n_mask_ls=None,
                              ):

  assert gpu_mode in GPU_MODE_SUPPORTED, "ERROR gpu_mode not in {}".format(str(GPU_MODE_SUPPORTED))
  assert py_script in AVAILABLE_TRAINING_EVAL_SCRIPT
  params = []
  labels = []
  default = []
  info_default = []

  if py_script == "train_evaluate_bert_normalizer":
    # we preprocess arguments : fill them in a dictionary in order to handle default None --> set to [None] (will call default in argparse )
    args_avail = OrderedDict()
    for arg in ARGS_AVAILABLE_PER_MODEL[py_script]:
      #TODO : all argument name should be normalize
      for lab in ["train", "dev", "test"]:
        if arg.startswith(lab):
          arg = lab
      args_avail[arg + "_ls"] = eval(arg + "_ls") if eval(arg + "_ls") is not None else [None]
      printing("WARNING : missing {} for script {} so setting it to [None]".format(arg+"_ls", py_script),
               verbose=1, verbose_level=1)
        #assert eval(arg+"_ls") is not None, "ERROR : missing {} for script {}".format(arg+"_ls", py_script)

  assert len(train_ls) == len(dev_ls), "ERROR train_ls is {} dev_ls {} : they should be same length".format(train_ls, dev_ls)
  assert len(tasks_ls) == len(train_ls), "ERROR tasks_ls {} and train_ls {} should be same lenght ".format(tasks_ls, train_ls)
  assert len(train_ls) == len(test_ls), "ERROR len train {} test {} train_ls is {} test_ls {} :" \
                                        " they should be same length ".format(len(train_ls), len(test_ls),
                                                                              train_ls, test_ls)
  if batch_size_ls is None:
    batch_size_ls = [DEFAULT_BATCH_SIZE]
    default.append(("batch_size", batch_size_ls[0]))
  if lr_ls is None:
    lr_ls = [DEFAULT_LR]
  if scale_ls is None:
    scale_ls = [DEFAULT_SCALE]
  if shared_context_ls is None:
    shared_context_ls = [DEFAULT_SHARED_CONTEXT]
    default.append(("shared_context", shared_context_ls[0]))
  if word_embed_init_ls is None:
    word_embed_init_ls = [DEFAULT_WORD_EMBED_INIT]
  if dir_word_encoder_ls is None:
    dir_word_encoder_ls = [DEFAULT_DIR_WORD_ENCODER]
    default.append(("dir_word_encoder", dir_word_encoder_ls[0]))
  assert len(dir_word_encoder_ls) == 1, "ERROR : only dir_word_encoder 2 allowed for Now (for loop nesting problem)"
  if char_src_attention_ls is None:
    char_src_attention_ls = [DEFAULT_CHAR_SRC_ATTENTION]
    default.append(("char_src_attention", char_src_attention_ls[0]))
  if dir_sent_encoder_ls is None:
    dir_sent_encoder_ls = [DEFAULT_DIR_SENT_ENCODER]
    default.append(("dir_sent_encoder", dir_sent_encoder_ls[0]))
  assert len(dir_sent_encoder_ls) == 1 and dir_sent_encoder_ls[0] == 2 , "ERROR : only dir_sent_encoder 2 allowed for Now (for loop nesting problem)"
  if clipping_ls is None:
    clipping_ls = [DEFAULT_CLIPPING]
    default.append(("gradient_clipping", clipping_ls[0]))
  assert len(clipping_ls)==1, "ERROR : ckipping not allowed in grid search anymore cause too many paramters"
  if unrolling_word_ls is None:
    unrolling_word_ls = [DEFAULT_WORD_UNROLLING]
    default.append(("unrolling_word", unrolling_word_ls[0]))
  assert unrolling_word_ls[0] and len(unrolling_word_ls)==1, "ERROR : only unrolling True allowed for Now (for loop nesting problem)"
  if teacher_force_ls is None:
    teacher_force_ls = [DEFAULT_TEACHER_FORCE]
    default.append(("teacher_force", teacher_force_ls[0]))
  if word_decoding_ls is None:
    word_decoding_ls = [DEFAULT_WORD_DECODING]
    default.append(("word_decoding", word_decoding_ls[0]))
  if word_recurrent_cell_encoder_ls is None:
    word_recurrent_cell_encoder_ls = [DEFAULT_WORD_RECURRENT_CELL]
    default.append(("word_recurrent_cell_encoder", word_recurrent_cell_encoder_ls[0]))
    #if auxilliary_task_pos_ls is None:
  ##  auxilliary_task_pos_ls = [False]
  # default.append(("auxilliary_task_pos", auxilliary_task_pos_ls[0]))
  if stable_decoding_state_ls is None:
    stable_decoding_state_ls = [DEFAULT_STABLE_DECODING]
    default.append(("stable_decoding_state", stable_decoding_state_ls[0]))
  assert not stable_decoding_state_ls[0] and len(stable_decoding_state_ls)==1, "ERROR : only stable_decoding_state False allowed for Now (for loop nesting problem)"
  if word_embedding_projected_dim_ls is None:
    word_embedding_projected_dim_ls = [DEFAULT_WORD_EMBEDDING_PROJECTED]
    default.append(("word_embedding_projected_dim", word_embedding_projected_dim_ls[0]))
  if n_layers_sent_cell_ls is None:
    n_layers_sent_cell_ls = [DEFAULT_LAYERS_SENT_CELL]
  if word_embed_ls is None:
    word_embed_ls = [DEFAULT_WORD_EMBED]
    default.append(("word_embed", word_embed_ls[0]))
  if proportion_pred_train_ls is None:
    proportion_pred_train_ls = [DEFAULT_PROPORTION_PRED_TRAIN]
    default.append(("proportion_pred_train", proportion_pred_train_ls[0]))
  if tasks_ls is None or len(tasks_ls) == 0:
    tasks_ls = [DEFAULT_TASKS]
    default.append(("task", tasks_ls[0]))
  if dropout_word_encoder_cell_ls is None:
    dropout_word_encoder_cell_ls = [DEFAULT_DROPOUT_WORD_ENCODER_CELL]
    default.append(("drop_out_word_encoder", dropout_word_encoder_cell_ls[0]))
  if attention_tagging_ls is None:
    attention_tagging_ls = [DEFAULT_ATTENTION_TAGGING]
    default.append(("attention_tagging", attention_tagging_ls[0]))
  if n_layers_word_encoder_ls is None:
    n_layers_word_encoder_ls = [DEFAULT_LAYER_WORD_ENCODER]
    default.append(("n_layers_word_encoder", n_layers_word_encoder_ls[0]))

  assert len(n_layers_word_encoder_ls) == 1, "ERROR n_layers_word_encoder_ls should be len 1 {}".format(n_layers_word_encoder_ls)

  if mode_word_encoding_ls is None:
    mode_word_encoding_ls = [DEFAULT_MODE_WORD_ENCODING] #"mode_word_encoding"
    default.append(("mode_word_encoding", mode_word_encoding_ls[0]))
  if char_level_embedding_projection_dim_ls is None:
    char_level_embedding_projection_dim_ls = [DEFAULT_CHAR_LEVEL_EMBEDDING_PROJECTION]
    default.append(("char_level_embedding_projection_dim", char_level_embedding_projection_dim_ls[0]))
  assert len(char_level_embedding_projection_dim_ls)==1, "ERROR : only supported 1 choice"
  if multi_task_loss_ponderation_ls is None:
    multi_task_loss_ponderation_ls = [DEFAULT_MULTI_TASK_LOSS_PONDERATION]
    default.append(("multi_task_loss_ponderation", multi_task_loss_ponderation_ls[0]))
  if dropout_input_ls is None:
    dropout_input_ls = [0]
    default.append(("dropout_input", dropout_input_ls[0]))
  if checkpointing_metric_ls is None:
    checkpointing_metric_ls = ["loss-dev-all" for _ in tasks_ls]
    default.append(("checkpointing_metric", checkpointing_metric_ls[0]))

  assert len(checkpointing_metric_ls) == len(test_ls),\
    "ERROR checkpointing_metric {} and test_ls {} should be same len".format(checkpointing_metric_ls, test_ls)

  for def_ in default:

    info_default.append((def_[0], def_[1])) #" "+str(def_[0])+","+str(def_[0])
    if py_script=="train_evaluate_run":
      printing("GRID : {} argument defaulted to {} ", var=[str(def_)[:-6], def_], verbose=0, verbose_level=0)
  # dic_grid will be used for logging (used for reports)
  if py_script == "train_evaluate_run":
    dic_grid = {"batch_size": batch_size_ls,# "auxilliary_task_norm_not_norm": auxilliary_task_norm_not_norm_ls,
                "shared_context": shared_context_ls,
                "lr": lr_ls, "word_embed_init": word_embed_init_ls, "dir_word_encoder": dir_word_encoder_ls,
                "char_src_attention": char_src_attention_ls,
                "dir_sent_encoder": dir_sent_encoder_ls, "gradient_clipping": clipping_ls,
                "unrolling_word": unrolling_word_ls,
                "word_decoding": word_decoding_ls, #"auxilliary_task_pos": auxilliary_task_pos_ls,
                "stable_decoding_state": stable_decoding_state_ls,
                "word_embedding_projected_dim": word_embedding_projected_dim_ls,
                "n_layers_sent_cell": n_layers_sent_cell_ls,
                "word_recurrent_cell_encoder": word_recurrent_cell_encoder_ls,
                "teacher_force": teacher_force_ls, "proportion_pred_train": proportion_pred_train_ls,
                "dropout_word_encoder_cell": dropout_word_encoder_cell_ls,
                "attention_tagging": attention_tagging_ls, "mode_word_encoding": mode_word_encoding_ls,
                "char_level_embedding_projection_dim": char_level_embedding_projection_dim_ls,
                "n_layers_word_encoder": n_layers_word_encoder_ls,
                "multi_task_loss_ponderation": multi_task_loss_ponderation_ls,
                "tasks": tasks_ls, "dropout_input": dropout_input_ls, "checkpointing_metric": checkpointing_metric_ls,
                "word_embed": word_embed_ls}

  elif py_script == "train_evaluate_bert_normalizer":
    dic_grid = OrderedDict()
    for args in ARGS_AVAILABLE_PER_MODEL[py_script]:
      _args = args
      for lab in ["train", "dev", "test"]:
        if args.startswith(lab):
          args = lab
          _args = lab+"_path"
      if _args != "tasks" and _args not in ["train_path", "dev_path", "test_path"]:
        dic_grid[_args] = args_avail[args+"_ls"]
      elif _args == "tasks":
        assert len(list(set(eval(_args+"_ls")[0]) & set(["normalize", "pos"]))) > 0, \
          "ERROR : only normalize, pos supported so far {}".format(eval(_args+"_ls"))
        #dic_grid[_args] = args_avail[_args + "_ls"]

    def sanity_check_args(py_script, dic_grid, train_ls, dev_ls, test_ls, tasks_ls):
      if py_script == "train_evaluate_bert_normalizer":
        for strat in dic_grid["fine_tuning_strategy"]:
          assert strat in AVAILABLE_BERT_FINE_TUNING_STRATEGY, \
            "ERROR strat {} not supported {}".format(strat, AVAILABLE_BERT_FINE_TUNING_STRATEGY)
        if isinstance(dic_grid["lr"][0], dict):
          assert dic_grid["fine_tuning_strategy"][0] == "flexible_lr" and len(dic_grid["fine_tuning_strategy"]) == 1, \
            "ERROR {} should be = flexible_lr".format(dic_grid["fine_tuning_strategy"])
        assert len(tasks_ls) == len(train_ls), "ERROR : GRID search : should have as many task(s for multitask) than train_path ls"
        assert len(tasks_ls) == len(dev_ls), "ERROR : GRID search : should have as many task(s for multitask) than dev_path ls"
        assert len(tasks_ls) == len(test_ls), "ERROR : should have as many task(s for multitask) than test ls "
        for train_sets, dev_sets, test_sets_ls, tasks in zip(train_ls, dev_ls, test_ls, tasks_ls):
          assert len(train_sets) == len(tasks), "ERROR : we should have one training set per task (no simulatnuous " \
                                                "training allowed for now but have tasks:{} and train_path:{}".format(tasks, train_sets)
          assert len(dev_sets) == len(tasks), "ERROR : we should have one dev set per task (no simulatnuous " \
                                              "training allowed for now but have tasks:{} and dev_path:{}".format(tasks,dev_sets)
          assert len(test_sets_ls[0].split(",")) == len(tasks), "ERROR not at least one test set per tasks {}".format(tasks)

    sanity_check_args(py_script, dic_grid, train_ls, dev_ls, test_ls, tasks_ls)
    list_of_list_of_args = [lis_values for arg_dic, lis_values in dic_grid.items()]

  ind_model = 0

  if py_script == "train_evaluate_bert_normalizer":
    arg_free_combination = list(itertools.product(*list_of_list_of_args))
    printing("GRID : running free combination of argument !! ", verbose_level=1, verbose=1)
    param0 = OrderedDict()
    # TODO : do the same for train_evaluate_run
    # for each set of training set, dev set, test and tasks : we run do a grid combination
    for train_sets, dev_sets, test_sets_ls, tasks in zip(train_ls, dev_ls, test_ls, tasks_ls):
      param0["train_path"] = train_sets
      param0["dev_path"] = dev_sets
      param0["test_path"] = test_sets_ls
      param0["tasks"] = tasks
      for combination in arg_free_combination:
        assert len(combination) == (len(list(dic_grid.keys())))
        for argument, arg_value in zip(list(dic_grid.keys()), combination):
          param0[argument] = arg_value
      #assert len(test_ls) == 1, "ONLY 1 task supported "
      #param0["test_path"] = test_ls[0]
        params.append(param0.copy())
        labels.append("{}-model_{}".format(grid_label, ind_model))
        ind_model += 1
  elif py_script == "train_evaluate_run":
    for batch in batch_size_ls:
      #for aux in auxilliary_task_norm_not_norm_ls:
      for lr in lr_ls:
        for shared_context in shared_context_ls:
          for scale in scale_ls:
            if shared_context == "sent":
              scale_sent_context = 1
              scale_word = 1
              scaled_output_dim = 1
            else:
              scale_sent_context, scale_word= scale, scale
              scaled_output_dim = max(int(scale/2), 1) if max(int(scale/2), 1) < 10 else 10
              scale = 1
            #for dir_word_encoder in dir_word_encoder_ls:
              printing("GRID : generating arg specific to {}", var=["train_evaluate_run"], verbose=1, verbose_level=1)
              for char_src_attention in char_src_attention_ls:
                #for dir_sent_encoder in dir_sent_encoder_ls:
                #for clipping in clipping_ls:
                #for unrolling_word in unrolling_word_ls:
                for word_decoding in word_decoding_ls:
                # for auxilliary_task_pos in auxilliary_task_pos_ls:
                  #for stable_decoding_state in stable_decoding_state_ls:
                  for word_embed in word_embed_ls:
                    if not word_embed:
                      _word_embedding_projected_dim_ls = [None]
                      _word_embed_init_ls = [None]
                      _mode_word_encoding_ls = ["cat"]
                      printing("GRID WARNING as word_embed False : argument word_embed projection, "
                               "initialization argument mode word cat cause no word embed", verbose=1, verbose_level=1)
                    else:
                      _word_embed_init_ls = word_embed_init_ls
                      _word_embedding_projected_dim_ls = word_embedding_projected_dim_ls
                      _mode_word_encoding_ls = mode_word_encoding_ls
                    for word_embed_init in _word_embed_init_ls:
                      for word_embedding_projected_dim in _word_embedding_projected_dim_ls:
                        for n_layers_sent_cell in n_layers_sent_cell_ls:
                          for proportion_pred_train in proportion_pred_train_ls:
                            #for tasks in tasks_ls:
                            for teacher_force in teacher_force_ls:
                              for word_recurrent_cell_encoder in word_recurrent_cell_encoder_ls:
                                for dropout_word_encoder_cell in dropout_word_encoder_cell_ls:
                                  for attention_tagging in attention_tagging_ls:
                                    #for n_layers_word_encoder in n_layers_word_encoder_ls:
                                    #for char_level_embedding_projection_dim in char_level_embedding_projection_dim_ls:
                                    for mode_word_encoding in _mode_word_encoding_ls:
                                      for multi_task_loss_ponderation in multi_task_loss_ponderation_ls:
                                        for dropout_input in dropout_input_ls:
                                          for tasks, train, dev, test, checkpointing_metric in zip(tasks_ls, train_ls, dev_ls, test_ls, checkpointing_metric_ls):
                                            param0 = param.copy()
                                            ind_model += 1

                                            param0["train_path"] = train
                                            param0["dev_path"] = dev
                                            param0["test_path"] = test
                                            param0["checkpointing_metric"] = checkpointing_metric
                                            param0["scoring_func"] = scoring_func
                                            param0["batch_size"] = batch
                                            param0["mode_word_encoding"] = mode_word_encoding
                                            param0["char_level_embedding_projection_dim"] = char_level_embedding_projection_dim_ls[0]
                                            #param0["auxilliary_task_norm_not_norm"] = aux
                                            param0["shared_context"] = shared_context
                                            param0["word_recurrent_cell_encoder"] = word_recurrent_cell_encoder
                                            param0["lr"] = lr
                                            param0["word_embed_init"] = word_embed_init
                                            param0["dropout_word_encoder_cell"] = dropout_word_encoder_cell
                                            param0["hidden_size_encoder"] = int(param0["hidden_size_encoder"] * scale *scale_word)
                                            param0["hidden_size_sent_encoder"] = int(param0["hidden_size_sent_encoder"] * scale * scale_sent_context)
                                            param0["hidden_size_decoder"] = int(param0["hidden_size_decoder"] * scale)
                                            param0["output_dim"] *= int(scale * scaled_output_dim) + 1
                                            param0["dir_word_encoder"] = dir_word_encoder_ls[0]
                                            param0["char_src_attention"] = char_src_attention
                                            param0["unrolling_word"] = unrolling_word_ls[0]
                                            param0["dir_sent_encoder"] = dir_sent_encoder_ls[0]
                                            param0["n_layers_sent_cell"] = n_layers_sent_cell
                                            param0["gradient_clipping"] = clipping_ls[0]
                                            param0["teacher_force"] = teacher_force
                                            param0["word_decoding"] = word_decoding
                                            param0["char_decoding"] = not word_decoding
                                            #param0["auxilliary_task_pos"] = auxilliary_task_pos
                                            param0["dense_dim_auxilliary_pos"] = 0 #if not "pos" in tasks else 0
                                            param0["dense_dim_auxilliary_pos_2"] = 0 #if not "pos" in tasks else 100

                                            param0["stable_decoding_state"] = stable_decoding_state_ls[0]
                                            param0["init_context_decoder"] = not param0["stable_decoding_state"]
                                            param0["activation_char_decoder"] = "nn.LeakyReLU"
                                            param0["activation_word_decoder"] = "nn.LeakyReLU"
                                            param0["tasks"] = tasks
                                            # default
                                            #param0["dropout_bridge"] = 0.1
                                            param0["word_embed"] = word_embed
                                            if word_embed_init is not None and word_embed:
                                              param0["word_embedding_dim"] = REPO_W2V[word_embed_init]["dim"]
                                            elif word_embed:
                                              param0["word_embedding_dim"] = 300
                                            else:
                                              param0["word_embedding_dim"] = 0
                                            param0["dense_dim_word_pred"] = 300 if word_decoding else None
                                            param0["dense_dim_word_pred_2"] = 300 if word_decoding else None
                                            param0["dense_dim_word_pred_3"] = 100 if word_decoding else None
                                            param0["word_embedding_projected_dim"] = word_embedding_projected_dim if param0["word_embed"] else None
                                            param0["proportion_pred_train"] = proportion_pred_train
                                            param0["gpu"] = get_gpu_id(gpu_mode, gpus_ls, 1)
                                            param0["attention_tagging"] = attention_tagging
                                            param0["n_layers_word_encoder"] = n_layers_word_encoder_ls[0]
                                            param0["multi_task_loss_ponderation"] = multi_task_loss_ponderation
                                            param0["dropout_input"] = dropout_input

                                            params.append(param0)
                                            labels.append("{}-model_{}".format(grid_label, ind_model))

  KEEP_ONLY_REMOVE = ["multi_task_loss_ponderation"]

  studied_vars = []
  fixed_vars = []
  printing("GRID HYPARAMETERS INIT {}", var=param, verbose=1, verbose_level=1)
  for var, vals in dic_grid.items():
    if var == "proportion_pred_train":
      if None in vals:
        vals[vals.index(None)] = 0
    if len(vals) > 1 or var in KEEP_ONLY_REMOVE:
      printing("GRID HYPERPARAMETERS : analysed variables ", var=[var, vals], verbose=1, verbose_level=1)
      studied_vars.append(var)
      if var not in KEEP_ONLY_REMOVE:
        print("GRID_INFO values ", var, " ".join([str(val) for val in vals]))
    else:
      printing("GRID HYPERPARAMETERS : fixed {} {} ", var=[var, vals], verbose=1, verbose_level=1)
      if var in KEEP_ONLY_REMOVE:
        continue
      fixed_vars.append((var, vals[0] if var != "word_embed_init" else REPO_W2V[vals[0]]["label"]))
  # grid information
  to_enrich = " ".join([a for a, _ in fixed_vars]) + " " + " ".join(studied_vars)
  if len(train_ls) > 1:
    studied_vars += ["train_path", "tasks"]
  to_analysed = " ".join(studied_vars)
  to_keep_only = " ".join([a + "," + str(b) for a, b in fixed_vars if a not in ["train_path", "dev_path"]])

  try:
    # TODO : this should be factorized with what is in args.json
    train_data_label = "|".join([REPO_DATASET[train_paths] for _train_path in train_ls for train_paths in _train_path])
    dev_data_label = "|".join([REPO_DATASET[dev_path] for _dev_path in dev_ls for dev_path in _dev_path])
    to_keep_only += " train_path,"+train_data_label+" dev_path,"+dev_data_label
  except Exception as e:
    print(e)
    print("ERROR", train_ls)
    printing("WARNING : train and dev_path fail to be label to be added to keep_only ", verbose_level=1, verbose=1)

  if printout_info_var:
    metric_add_ls = []
    for tasks in tasks_ls:
      for task in tasks:
        metric_add_ls.extend(TASKS_2_METRICS_STR[task])
    metric_add = " ".join(list(set(metric_add_ls)))
    print("{} {}".format(REPORT_FLAG_VARIABLES_EXPAND_STR, metric_add))
    print("{} {} SEED".format(REPORT_FLAG_VARIABLES_ENRICH_STR, to_enrich))
    print("{} {} SEED".format(REPORT_FLAG_VARIABLES_ANALYSED_STR, to_analysed))
    print("{} {} ".format(REPORT_FLAG_VARIABLES_FIXED_STR, to_keep_only))

  return params, labels, info_default, studied_vars, fixed_vars
