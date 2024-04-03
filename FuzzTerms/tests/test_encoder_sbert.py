from fuzzterms import Encoder
from fuzzterms.encoders.sbert import SBertEncoder


def test_encoder_sbert(collection):
    assert collection.config.vss_backend == "sbert"
    encoder = Encoder.construct(collection)
    assert isinstance(encoder, SBertEncoder)
