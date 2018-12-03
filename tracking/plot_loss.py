import os
import matplotlib.pyplot as plt


def simple_plot(final_loss, loss_ls, epochs=None, V=None, seq_len=None, lr=None, save=False, show=True, prefix="test"):

    print("Final Loss {} ".format(final_loss))
    plt.title("Training Loss with {} lr".format(lr))
    plt.xlabel("epoch")
    plt.plot(loss_ls)
    dir_fig = os.path.join("/Users/benjaminmuller/Desktop/Work/INRIA/dev/mt_norm_parse/test/test_logs","{}-{}ep-{}V-{}lr-{}seq.png".format(prefix, epochs, V, lr, seq_len))
    if save:
        plt.savefig(dir_fig )
        print("Loss of the test saved to {} ".format(dir_fig))

    if show:
        print("Showing loss")
        plt.show()