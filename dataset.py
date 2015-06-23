import os

import numpy
from fuel import config
from fuel.datasets import IndexableDataset
from fuel.schemes import SequentialExampleScheme, ConstantScheme
from fuel.streams import DataStream
from fuel.transformers import Transformer, Batch


# class MakeRecurrent(Transformer):

#     def __init__(self, time_length, data_stream, target_source='targets'):
#         if len(data_stream.sources) > 1:
#             raise ValueError
#         super(MakeRecurrent, self).__init__(data_stream)
#         self.sources = self.sources + (target_source,)
#         self.time_length = time_length
#         self.sentence = []
#         self.index = 0

#     def get_data(self, request=None):
#         while not self.index < len(self.sentence) - self.time_length - 1:
#             self.sentence, = next(self.child_epoch_iterator)
#             print self.sentence.shape
#             self.index = 0
#         x = self.sentence[self.index:self.index + self.time_length]
#         target = self.sentence[
#             self.index + 1:self.index + self.time_length + 1]
#         self.index += self.time_length
#         return (x, target)


def get_data(dataset):
    if dataset == "wikipedia":
        path = os.path.join(config.data_path, 'wikipedia-text',
                            'char_level_enwik8.npz')
    elif dataset == "penntree":
        path = os.path.join(config.data_path, 'PennTreebankCorpus',
                            'char_level_penntree.npz')
    return numpy.load(path, 'rb')


def get_character(dataset):
    data = get_data(dataset)
    return data["vocab"]


def get_stream_char(dataset, which_set, time_length, mini_batch_size,
                    total_train_chars=None):
    data = get_data(dataset)
    dataset = data[which_set]
    if total_train_chars is None:
        total_train_chars = dataset.shape[0]

    nb_mini_batches = total_train_chars / (mini_batch_size * time_length)
    total_train_chars = nb_mini_batches * mini_batch_size * time_length

    dataset = dataset[:total_train_chars]

    dataset = dataset.reshape(
        mini_batch_size, total_train_chars / mini_batch_size)
    dataset = dataset.T

    targets_dataset = dataset[1:, :]
    targets_dataset = numpy.concatenate(
        (targets_dataset, numpy.zeros((1, mini_batch_size))), axis=0)

    dataset = dataset.reshape(
        total_train_chars / (mini_batch_size * time_length),
        time_length, mini_batch_size)
    targets_dataset = targets_dataset.reshape(
        total_train_chars / (mini_batch_size * time_length),
        time_length, mini_batch_size)
    # print dataset.shape
    # print targets_dataset.shape
    dataset = IndexableDataset({'features': dataset,
                                'targets': targets_dataset})
    stream = DataStream(dataset,
                        iteration_scheme=SequentialExampleScheme(
                            nb_mini_batches))
    # stream = MakeRecurrent(time_length, stream)
    return stream, total_train_chars


def get_minibatch_char(dataset, mini_batch_size,
                       time_length, total_train_chars=None):
    data = get_data(dataset)
    vocab_size = data['vocab_size']

    train_stream, train_num_examples = get_stream_char(
        dataset, "train", time_length, mini_batch_size, total_train_chars)
    valid_stream, valid_num_examples = get_stream_char(
        dataset, "valid", time_length, mini_batch_size)
    return train_stream, valid_stream, vocab_size

if __name__ == "__main__":
    # Test
    dataset = "penntree"
    time_length = 7
    mini_batch_size = 4

    voc = get_character(dataset)
    (train_stream, valid_stream, vocab_size) = get_minibatch_char(dataset,
                                                                  mini_batch_size,
                                                                  time_length)

    # stream, total_train_chars = get_stream_char(dataset, "train", time_length,
    #                                             mini_batch_size)
    # print(voc)
    iterator = train_stream.get_epoch_iterator()
    print(next(iterator))
    print(next(iterator))
    print(next(iterator))
