from sentence_transformers import SentenceTransformer
from fuzzterms import Encoder


class SBertEncoder(Encoder):
    name = "sbert"

    def __init__(self, collection):
        super().__init__(collection)
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(
                model_name_or_path=self.config.vss_model,
                device=self.config.vss_device,
            )
        return self._model

    def encode(self, sentences):
        return self.model.encode(
            sentences,
            device=self.collection.config.vss_device,
        )
