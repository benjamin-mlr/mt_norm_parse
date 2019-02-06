import torch.nn as nn
import torch
import pdb
from torch.autograd import Variable
import torch.nn.functional as F
import numpy as np

import time
EPSILON = 1e-5



class Attention(nn.Module):

    def __init__(self,  hidden_size_word_decoder,
                 char_embedding_dim, hidden_size_src_word_encoder, time=False,
                 method="general",use_gpu=False):

        super(Attention, self).__init__()
        self.time = time
        self.hidden_size_word_decoder = hidden_size_word_decoder
        self.attn = nn.Linear(hidden_size_word_decoder ,#+ char_embedding_dim,
                              hidden_size_src_word_encoder)#+hidden_size, hidden_size) # CHANGE--> (compared to example) we (hidden_size * 2+hidden_size because we have the embedding size +  ..
        self.v = nn.Parameter(torch.FloatTensor(self.hidden_size_word_decoder))
        self.use_gpu = use_gpu
        self.method = method

    def score(self, char_state_decoder, encoder_output):
        if self.method == "concat":
            print("WARNING : Do not understand the self.v.dot + will cause shape error  ")
            energy = self.attn(torch.cat((char_state_decoder, encoder_output), 0))#CHANGE 0 instead of 1
            energy = self.v.dot(energy)
        elif self.method == "general":
            energy = self.attn(char_state_decoder)
            energy = energy.unsqueeze(-1)
            encoder_output = encoder_output.squeeze(-1)#.unsqueeze(1)
            #energy = encoder_output.matmul(energy)

            energy = torch.bmm(encoder_output, energy)
            #energy = energy.squeeze(1).squeeze(1)
            energy = energy.squeeze(-1)
        elif self.method == "bahadanu":
            #TODO
            pass
            #energy = encoder_output.dot(energy)
        return energy

    def forward(self, char_state_decoder, encoder_outputs, word_src_sizes=None):
        max_word_len_src = encoder_outputs.size(1)
        this_batch_size = encoder_outputs.size(0)
        attn_energies = Variable(torch.zeros(this_batch_size, max_word_len_src)) # B x S
        # we loop over all the source encoded sequence (of character) to compute the attention weight
        # is the loop on the batch necessary
        #for batch in range(this_batch_size):
        # index of src word for masking
        #batch_diag = torch.empty(encoder_outputs.size(1), len(word_src_sizes),len(word_src_sizes))
        #for word in range(len(encoder_outputs.size(1))):
            #score_index = np.array([i for i in range(len(word)) > word_src_sizes[word]])
            #diag = torch.diag(score_index).float()
            #batch_diag[word,:,:] = diag
        #
        #scores_energy = diag.matmul(scores_energy)
        attn_energies = self.score(char_state_decoder[:, :], encoder_outputs.squeeze(1))
        # scores_energy shaped : number of decoded word (batch x len_sent max) times n_character max src
        # we have a attention energy for the current decoding character for each src word target word pair
        #attn_energies[:, char_src] = diag.matmul(scores_energy)
        if False:
            for char_src in range(max_word_len_src):
                # TODO : ADD MASKING HERE : SET TO 0 when char_src above SIZE of source encoder_outputs
                # encoder_outputs[batch, char_src] : contextual character
                #   - embedding of character ind char_src at batch (word level context) of the source word
                # char_state_decoder[batch, :] : state of the decoder for batch ind (embedding)
                score_index = char_src+1 < word_src_sizes

                scores_energy = self.score(char_state_decoder[:, :],
                                           encoder_outputs[:, char_src]) # CHANGE : no need of unsquueze ?
                pdb.set_trace()
                # masking end of src words
                diag = torch.diag(score_index).float()
                #diag.dtype(dtype=torch.float)
                if scores_energy.is_cuda:
                    diag = diag.cuda()
                attn_energies[:, char_src] = diag.matmul(scores_energy)
                #attn_energies[:, char_src] = torch.diag(score_index).matmul(attn_energies[:, char_src])
                #attn_energies[char_src+1 >= word_src_sizes, char_src] = -1e6
                # we zero the softmax by assigning an ennergy of -inf
        softmax = F.softmax(attn_energies)
        try:
            assert ((softmax.sum(dim=1) - torch.ones(softmax.size(0))) < EPSILON).all(), "ERROR : softmax not softmax"
        except:
            print("SOFTMAX is not softmax : softmax.size(0)")
        #  we do masking here : word that are only 1 len (START character) :
        #  we set their softmax to 0 so that their context vector is
        #  Q? is it useful
        #softmax_clone = softmax.clone()
        diag_sotm = torch.diag(word_src_sizes != 1).float()

        if softmax.is_cuda:
            diag_sotm = diag_sotm.cuda()
        # masking empty words
        softmax_ = diag_sotm.matmul(softmax) # equivalent to softmax[word_src_sizes == 1, :] = 0. #assert (softmax_2==softmax).all()
        softmax_ = softmax_.unsqueeze(1)
        return softmax_

