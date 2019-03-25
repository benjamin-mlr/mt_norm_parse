import argparse
from env.default_hyperparameters import *


def args_train(mode="command_line"):
    """NB : arguments default used variables to be aligned with grid_tool default
    (because : default in grid tools means grid_list arguments is len 1 means not passed to argt_train means call default)
    (could thing of a more integrated way to do it )"""
    assert mode in ["command_line", "script"], "mode should be in '[command_line, script]"

    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden_size_encoder", type=int, required=True, help="display a square of a given number")
    parser.add_argument("--hidden_size_sent_encoder", required=True, type=int, help="display a square of a given number")
    parser.add_argument("--hidden_size_decoder", required=True, type=int, help="display a square of a given number")

    parser.add_argument("--word_embed", type=int, default=DEFAULT_WORD_EMBED, help="display a square of a given number")
    parser.add_argument("--word_embedding_dim", required=True, type=int, help="display a square of a given number")
    parser.add_argument("--word_embedding_projected_dim", default=DEFAULT_WORD_EMBEDDING_PROJECTED, type=int, help="display a square of a given number")
    parser.add_argument("--output_dim", required=True, type=int, help="display a square of a given number")
    parser.add_argument("--char_embedding_dim",required=True, type=int, help="display a square of a given number")

    parser.add_argument("--mode_word_encoding", default=DEFAULT_MODE_WORD_ENCODING, type=str, help="display a square of a given number")
    parser.add_argument("--char_level_embedding_projection_dim", default=DEFAULT_CHAR_LEVEL_EMBEDDING_PROJECTION, type=int, help="display a square of a given number")

    parser.add_argument("--batch_size", default=2, type=int, help="display a square of a given number")
    parser.add_argument("--epochs", default=1, type=int, help="display a square of a given number")

    parser.add_argument("--dropout_sent_encoder", default=0, type=float, help="display a square of a given number")
    parser.add_argument("--dropout_word_encoder_cell", default=DEFAULT_DROPOUT_WORD_ENCODER_CELL, type=float, help="display a square of a given number")
    parser.add_argument("--dropout_word_decoder", default=0, type=float, help="display a square of a given number")
    parser.add_argument("--drop_out_word_encoder_out", default=0, type=float, help="display a square of a given number")
    parser.add_argument("--drop_out_sent_encoder_out", default=0, type=float, help="display a square of a given number")
    parser.add_argument("--dropout_bridge", default=0, type=float, help="display a square of a given number")
    parser.add_argument("--drop_out_char_embedding_decoder", default=0, type=float, help="display a square of a given number")

    parser.add_argument("--n_layers_word_encoder", default=DEFAULT_LAYER_WORD_ENCODER, type=int, help="display a square of a given number")
    parser.add_argument("--n_layers_sent_cell", default=DEFAULT_LAYERS_SENT_CELL, type=int, help="display a square of a given number")

    parser.add_argument("--dir_sent_encoder", default=DEFAULT_DIR_SENT_ENCODER, type=int, help="display a square of a given number")

    parser.add_argument("--word_recurrent_cell_encoder", default=DEFAULT_WORD_RECURRENT_CELL, help="display a square of a given number")
    parser.add_argument("--word_recurrent_cell_decoder", default="LSTM", help="display a square of a given number")

    parser.add_argument("--dense_dim_auxilliary", default=None, type=int, help="display a square of a given number")
    parser.add_argument("--dense_dim_auxilliary_2", default=None, type=int, help="displaqy a square of a given number")

    parser.add_argument("--unrolling_word", default=DEFAULT_WORD_UNROLLING, type=int, help="display a square of a given number")

    parser.add_argument("--char_src_attention", default=DEFAULT_CHAR_SRC_ATTENTION, type=int, help="display a square of a given number")
    parser.add_argument("--dir_word_encoder", default=DEFAULT_DIR_WORD_ENCODER, type=int, help="display a square of a given number")
    parser.add_argument("--weight_binary_loss", default=1, type=float, help="display a square of a given number")
    parser.add_argument("--shared_context", default=DEFAULT_SHARED_CONTEXT, help="display a square of a given number")

    parser.add_argument("--policy", default=None, type=int, help="display a square of a given number")
    parser.add_argument("--lr", default=DEFAULT_LR, type=float, help="display a square of a given number")
    parser.add_argument("--gradient_clipping", type=int, default=DEFAULT_CLIPPING, help="display a square of a given number")
    parser.add_argument("--teacher_force", type=int, default=DEFAULT_TEACHER_FORCE, help="display a square of a given number")
    parser.add_argument("--proportion_pred_train", type=int, default=DEFAULT_PROPORTION_PRED_TRAIN, help="display a square of a given number")

    parser.add_argument("--stable_decoding_state", type=int, default=DEFAULT_STABLE_DECODING, help="display a square of a given number")
    parser.add_argument("--init_context_decoder", type=int, default=not DEFAULT_STABLE_DECODING, help="display a square of a given number")
    parser.add_argument("--optimizer", default="adam", help="display a square of a given number ")

    parser.add_argument("--word_decoding", default=DEFAULT_WORD_DECODING, type=int, help="display a square of a given number ")

    parser.add_argument("--attention_tagging", default=DEFAULT_ATTENTION_TAGGING, type=int, help="display a square of a given number ")

    parser.add_argument("--dense_dim_word_pred", type=int, default=None, help="display a square of a given number ")
    parser.add_argument("--dense_dim_word_pred_2", type=int, default=None, help="display a square of a given number ")
    parser.add_argument("--dense_dim_word_pred_3", type=int, default=0, help="display a square of a given number ")

    parser.add_argument("--word_embed_init", default=DEFAULT_WORD_EMBED_INIT,help="display a square of a given number")
    parser.add_argument("--char_decoding", type=int, default=True, help="display a square of a given number")

    parser.add_argument("--dense_dim_auxilliary_pos",type=int, default=None, help="display a square of a given number")
    parser.add_argument("--dense_dim_auxilliary_pos_2",type=int, default=None, help="display a square of a given number")
    parser.add_argument("--activation_char_decoder", default=None, help="display a square of a given number")
    parser.add_argument("--activation_word_decoder", default=None, help="display a square of a given number")
    parser.add_argument('--tasks', nargs='+', help='<Required> Set flag', default=DEFAULT_TASKS)

    parser.add_argument("--train_path", required=mode == "command_line", help="display a square of a given number")
    parser.add_argument("--dev_path", required=mode == "command_line", help="display a square of a given number")
    parser.add_argument('--test_paths', nargs='+', help='<Required> Set flag', default=None)

    parser.add_argument("--pos_specific_path", default=None, type=str, help="display a square of a given number")
    parser.add_argument("--expand_vocab_dev_test", default=True, help="display a square of a given number")

    parser.add_argument("--multi_task_loss_ponderation", type=str, default="all", help="display a square of a given number")

    parser.add_argument("--model_id_pref", required=mode == "command_line", help="display a square of a given number")
    parser.add_argument("--overall_label", default="DEFAULT", help="display a square of a given number")
    parser.add_argument("--overall_report_dir", required=mode == "command_line", help="display a square of a given number")
    parser.add_argument("--debug", action="store_true", help="display a square of a given number")
    parser.add_argument("--warmup", action="store_true", help="display a square of a given number")
    parser.add_argument("--verbose", default=1, type=int,help="display a square of a given number")

    parser.add_argument("--scoring_func", default="exact_match", type=str, help="display a square of a given number")

    parser.add_argument("--dropout_input", default=0, type=float, help="display a square of a given number")

    parser.add_argument("--gpu", default=None, type=str, help="display a square of a given number")

    args = parser.parse_args()

    if not args.word_embed:
        args.word_embedding_dim = 0


    return args
