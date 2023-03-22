# Bug with PyTorch source code makes torch.tensor as not callable for pylint.
# We also skip protected-access since we test the encoder and decoder step
# pylint: disable=not-callable, protected-access

import os
import unittest
from unittest import skipIf
from unittest.mock import patch

import torch

from deepparse import CACHE_PATH
from deepparse.network import FastTextSeq2SeqModel
from ..integration.base import Seq2SeqIntegrationTestCase


@skipIf(
    not os.path.exists(os.path.join(os.path.expanduser("~"), ".cache", "deepparse", "cc.fr.300.bin")),
    "download of model too long for test in runner",
)
class FastTextSeq2SeqIntegrationTest(Seq2SeqIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super(FastTextSeq2SeqIntegrationTest, cls).setUpClass()
        cls.models_setup(model_type="fasttext", cache_dir=cls.path)
        cls.a_retrain_model_path = os.path.join(cls.path, cls.retrain_file_name_format.format("fasttext") + ".ckpt")

    def setUp(self) -> None:
        super().setUp()
        # will load the weights if not local
        self.encoder_input_setUp("fasttext", self.a_cpu_device)

        self.a_target_vector = torch.tensor([[0, 1, 1, 4, 5, 8], [1, 0, 3, 8, 0, 0]], device=self.a_cpu_device)

    def test_whenForwardStep_thenStepIsOk(self):
        self.seq2seq_model = FastTextSeq2SeqModel(
            self.cache_dir, self.a_cpu_device, output_size=self.number_of_tags, use_torch_compile=False
        )
        # forward pass for two address: "["15 major st london ontario n5z1e1", "15 major st london ontario n5z1e1"]"
        self.decoder_input_setUp()

        predictions = self.seq2seq_model.forward(self.to_predict_tensor, self.a_lengths_list)

        self.assert_output_is_valid_dim(predictions, output_dim=self.number_of_tags)

    def test_whenForwardStepWithTarget_thenStepIsOk(self):
        self.seq2seq_model = FastTextSeq2SeqModel(
            self.cache_dir, self.a_cpu_device, output_size=self.number_of_tags, use_torch_compile=False
        )
        # forward pass for two address: "["15 major st london ontario n5z1e1", "15 major st london ontario n5z1e1"]"
        self.decoder_input_setUp()

        predictions = self.seq2seq_model.forward(self.to_predict_tensor, self.a_lengths_list, self.a_target_vector)

        self.assert_output_is_valid_dim(predictions, output_dim=self.number_of_tags)

    def test_retrainedModel_whenForwardStep_thenStepIsOk(self):
        self.seq2seq_model = FastTextSeq2SeqModel(
            self.cache_dir,
            self.a_cpu_device,
            output_size=self.re_trained_output_dim,
            verbose=self.verbose,
            path_to_retrained_model=self.a_retrain_model_path,
        )
        # forward pass for two address: "["15 major st london ontario n5z1e1", "15 major st london ontario n5z1e1"]"
        self.decoder_input_setUp()

        predictions = self.seq2seq_model.forward(self.to_predict_tensor, self.a_lengths_list)

        self.assert_output_is_valid_dim(predictions, output_dim=self.re_trained_output_dim)

    def test_retrainedModel_whenForwardStepWithTarget_thenStepIsOk(self):
        self.seq2seq_model = FastTextSeq2SeqModel(
            self.cache_dir,
            self.a_cpu_device,
            output_size=self.re_trained_output_dim,
            verbose=self.verbose,
            path_to_retrained_model=self.a_retrain_model_path,
        )
        # forward pass for two address: "["15 major st london ontario n5z1e1", "15 major st london ontario n5z1e1"]"
        self.decoder_input_setUp()

        predictions = self.seq2seq_model.forward(self.to_predict_tensor, self.a_lengths_list, self.a_target_vector)

        self.assert_output_is_valid_dim(predictions, output_dim=self.re_trained_output_dim)

    @patch("deepparse.network.seq2seq.download_weights")
    def test_givenAnOfflineSeq2SeqModel_whenInit_thenDontCallDownloadWeights(self, download_weights_mock):
        # Test if functions latest_version and download_weights

        default_cache = CACHE_PATH

        self.seq2seq_model = FastTextSeq2SeqModel(
            default_cache, self.a_cpu_device, verbose=self.verbose, offline=True, use_torch_compile=False
        )

        download_weights_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
