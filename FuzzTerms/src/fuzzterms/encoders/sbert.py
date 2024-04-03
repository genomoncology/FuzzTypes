from sentence_transformers import SentenceTransformer
from fuzzterms import Encoder


class SBertEncoder(Encoder):
    name = "sbert"

    def __init__(self, collection):
        super().__init__(collection)

        self.model = SentenceTransformer(
            model_name_or_path=self.config.vss_model,
            device=self.config.vss_device,
        )

    def encode(self, sentences):
        return self.model.encode(
            sentences,
            device=self.collection.config.vss_device,
        )
