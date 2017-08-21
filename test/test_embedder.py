import unittest

import numpy as np
import tensorflow as tf
from nn.embedder import FixedWordEmbedder, shrink_embed


class MockLoader(object):
    def __init__(self, name, vec):
        self.name = name
        self.vec = vec

    def load_word_vec(self, name, voc):
        if name != self.name:
            raise ValueError()
        return self.vec


class TestEmbed(unittest.TestCase):

    def test_shrink_embed(self):
        with tf.Session().as_default():
            original_mat = np.arange(9).reshape((9, 1)).astype(np.float32)
            original_word_ix = [(np.array([[0, 3, 0], [8, 3, 8]]))]
            mat, word_ix = shrink_embed(original_mat, original_word_ix)
            self.assertEqual(list(mat.eval().ravel()), [0, 3, 8])
            self.assertEqual(list(word_ix[0].eval().ravel()), [0, 1, 0, 2, 1, 2])
            self.assertEqual(word_ix[0].eval().shape, original_word_ix[0].shape)

    def test_shrink_embed_rng(self):
        with tf.Session().as_default():
            n_words = 500
            original_mat = tf.constant(np.arange(n_words).reshape((n_words, 1)).astype(np.float32))
            for i in range(50):
                original_word_ix = [np.random.randint(0, n_words, (2, 5)),
                                    np.random.randint(0, n_words, (3, 5, 2))]
                mat, word_ix = shrink_embed(original_mat, original_word_ix)
                mat = mat.eval()
                self.assertTrue(np.array_equal(
                    mat[word_ix[0].eval().ravel()].reshape(word_ix[0].shape),
                    original_word_ix[0]))
                self.assertTrue(np.array_equal(
                    mat[word_ix[1].eval().ravel()].reshape(word_ix[1].shape),
                    original_word_ix[1]))

    def test_fixed_embed(self):
        loader = MockLoader("v1", dict(
            red=np.array([0, 1], dtype=np.float32),
            the=np.array([1, 1], dtype=np.float32),
            fish=np.array([1, 0], dtype=np.float32),
            one=np.array([1, 0], dtype=np.float32)))

        emb = FixedWordEmbedder("v1")
        emb.init(loader, {"red", "cat", "decoy", "one", "fish"})

        out = [emb.context_word_to_ix(x) for x in ["red", "one", "fish"]]
        self.assertEqual(set(out), {2, 3, 4})

        out = [emb.context_word_to_ix(x) for x in ["decoy", "??", "the"]]
        self.assertEqual(list(out), [1, 1, 1])

    # def test_partial_embed(self):
    #     loader = MockLoader("v1", dict(
    #         red=np.array([0, 1], dtype=np.float32),
    #         the=np.array([1, 1], dtype=np.float32),
    #         fish=np.array([1, 0], dtype=np.float32),
    #         one=np.array([1, 0], dtype=np.float32)))
    #
    #     test = [ParagraphAndQuestion(["one fish two fish".split(" ")],
    #                                  "red fish ?".split(" "),
    #                                  None, 0,0,0)]
    #
    #     emb = PartialTrainEmbedder("v1", word_count_th=0,
    #                                train_unknown=False,
    #                                train_context_th = ((0, 0),),
    #                                train_question_th = ((0, 0),),)
    #     emb.set_vocab(test, loader)
    #     self.assertEqual(set(emb.train_context_words), {"red", "one", "fish"})
    #
    #     emb = PartialTrainEmbedder("v1", word_count_th=2,
    #                                train_unknown=False,
    #                                train_context_th = ((0, 0),),
    #                                train_question_th = ((0, 0),),)
    #     emb.set_vocab(test, loader)
    #     self.assertEqual(set(emb.train_question_words), {"fish"})
    #     self.assertEqual(set(emb.train_question_words), {"fish"})
    #
    #     emb = PartialTrainEmbedder("v1", word_count_th=0,
    #                                train_unknown=False,
    #                                train_context_th = ((2, 0),),
    #                                train_question_th = ((1, 0),),)
    #     emb.set_vocab(test, loader)
    #     self.assertEqual(set(emb.train_context_words), {"fish"})
    #     self.assertEqual(set(emb.train_question_words), {"red", "fish"})