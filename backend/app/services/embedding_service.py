from __future__ import annotations

from hashlib import sha256
from typing import Protocol

from google import genai
from google.genai import types


class EmbeddingService(Protocol):
    def embed_texts(
        self,
        texts: list[str],
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        ...


class GeminiEmbeddingService:
    def __init__(self, api_key: str, model: str, output_dimensionality: int) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.output_dimensionality = output_dimensionality

    def embed_texts(
        self,
        texts: list[str],
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(
                taskType=task_type,
                outputDimensionality=self.output_dimensionality,
            ),
        )
        embeddings = [embedding.values or [] for embedding in response.embeddings or []]
        return validate_embeddings(embeddings, expected_dim=self.output_dimensionality)


class DeterministicEmbeddingService:
    def __init__(self, output_dimensionality: int = 768) -> None:
        self.output_dimensionality = output_dimensionality

    def embed_texts(
        self,
        texts: list[str],
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        return [self._embed(text, task_type) for text in texts]

    def _embed(self, text: str, task_type: str) -> list[float]:
        # 테스트용 embedding은 외부 API 없이도 차원/흐름을 검증하기 위한 deterministic vector다.
        # 실제 검색 품질에는 쓰지 않고 Gemini adapter와 같은 shape만 보장한다.
        values: list[float] = []
        seed = f"{task_type}:{text}".encode()
        counter = 0
        while len(values) < self.output_dimensionality:
            digest = sha256(seed + counter.to_bytes(4, "big")).digest()
            values.extend((byte / 127.5) - 1.0 for byte in digest)
            counter += 1
        return values[: self.output_dimensionality]


def validate_embeddings(
    embeddings: list[list[float]],
    *,
    expected_dim: int,
) -> list[list[float]]:
    for index, embedding in enumerate(embeddings):
        if len(embedding) != expected_dim:
            raise ValueError(
                f"embedding[{index}] dimension mismatch: "
                f"expected {expected_dim}, got {len(embedding)}"
            )
    return embeddings


def attach_embeddings_to_payloads(
    payloads: list[dict[str, object]],
    embedding_service: EmbeddingService,
    *,
    batch_size: int = 16,
) -> list[dict[str, object]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    enriched: list[dict[str, object]] = []
    for start in range(0, len(payloads), batch_size):
        batch = payloads[start : start + batch_size]
        # title과 heading_path를 같이 넣어 짧은 chunk도 검색 의도를 더 잘 담도록 한다.
        texts = [
            "\n".join(
                part
                for part in [
                    str(payload.get("title") or ""),
                    str(payload.get("heading_path") or ""),
                    str(payload["content"]),
                ]
                if part
            )
            for payload in batch
        ]
        embeddings = embedding_service.embed_texts(texts)
        if len(embeddings) != len(batch):
            # Gemini embedding API가 batch 일부만 반환하는 경우가 있어 live ingest는
            # 해당 batch를 버리지 않고 chunk 단위로 재시도해 누락 원인을 좁힌다.
            embeddings = [
                _embed_single_text(embedding_service, text, batch_start=start + offset)
                for offset, text in enumerate(texts)
            ]
        for payload, embedding in zip(batch, embeddings, strict=True):
            enriched_payload = dict(payload)
            enriched_payload["embedding"] = embedding
            enriched.append(enriched_payload)
    return enriched


def _embed_single_text(
    embedding_service: EmbeddingService,
    text: str,
    *,
    batch_start: int,
) -> list[float]:
    embeddings = embedding_service.embed_texts([text])
    if len(embeddings) != 1:
        raise ValueError(
            "embedding count mismatch after single retry: "
            f"payload index {batch_start}, expected 1, got {len(embeddings)}"
        )
    return embeddings[0]
