from fuzzterms.encoders.sbert import SBertEncoder


def test_encoder_sbert(collection):
    assert collection.config.vss_backend == "sbert"
    assert isinstance(collection.encoder, SBertEncoder)
