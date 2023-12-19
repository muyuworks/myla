from typing import List, Optional, Dict, Any
from ._embeddings import Embeddings

DEFAULT_BGE_INSTRUCTION_EN = "Represent this question for searching relevant passages: "

DEFAULT_BGE_INSTRUCTION_ZH = "为这个句子生成表示以用于检索相关文章："


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(
            self,
            model_name=None,
            model_kwargs: Optional[Dict[str, Any]] = {},
            encode_kwargs: Optional[Dict[str, Any]] = {},
            multi_process: bool = False,
            instruction: str = None
    ) -> None:
        super().__init__()
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs
        self.multi_process = multi_process

        if not self.model_name:
            raise ValueError("Can't found embeddings model, EMBEDDINGS_MODEL_NAME required.")

        self.instruction = instruction
        if not self.instruction:
            self.instruction = DEFAULT_BGE_INSTRUCTION_ZH if '-zh' in self.model_name else DEFAULT_BGE_INSTRUCTION_EN

        self.is_bge_model = 'bge' in self.model_name

        try:
            import sentence_transformers
        except ImportError as exc:
            raise ImportError(
                "Could not import sentence_transformers python package. "
                "Please install it with `pip install sentence_transformers`."
            ) from exc

        self.tansformer = sentence_transformers.SentenceTransformer(
            self.model_name, **self.model_kwargs
        )

    def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        import sentence_transformers

        instruction = self.instruction if 'instruction' not in kwargs else kwargs['instruction']
        print(instruction)
        texts = list(map(lambda x: (instruction if self.is_bge_model else '') + x.replace("\n", " "), texts))

        if self.multi_process:
            pool = self.tansformer.start_multi_process_pool()
            embeddings = self.tansformer.encode_multi_process(texts, pool)
            sentence_transformers.SentenceTransformer.stop_multi_process_pool(
                pool)
        else:
            embeddings = self.tansformer.encode(texts, **self.encode_kwargs)

        return embeddings.tolist()
