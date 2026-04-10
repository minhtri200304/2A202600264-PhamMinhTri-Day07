from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        if not text.strip():
            return []
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk]).strip()
            chunks.append(chunk)

        return chunks
        raise NotImplementedError("Implement SentenceChunker.chunk")


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        if not text.strip():
            return []
        return self._split(text.strip(), self.separators)
        raise NotImplementedError("Implement RecursiveChunker.chunk")

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [current_text[i:i + self.chunk_size]
                    for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]

        # fallback: split cứng theo chunk_size
        if sep == "":
            return [current_text[i:i + self.chunk_size]
                    for i in range(0, len(current_text), self.chunk_size)]

        parts = current_text.split(sep)

        chunks = []
        buffer = ""

        for part in parts:
            candidate = buffer + (sep if buffer else "") + part

            if len(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                if buffer:
                    chunks.extend(self._split(buffer, remaining_separators[1:]))
                buffer = part

        if buffer:
            chunks.extend(self._split(buffer, remaining_separators[1:]))

        return chunks
        raise NotImplementedError("Implement RecursiveChunker._split")


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)

    raise NotImplementedError("Implement compute_similarity")


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        fixed = FixedSizeChunker(chunk_size=chunk_size)
        sentence = SentenceChunker()
        recursive = RecursiveChunker(chunk_size=chunk_size)

        results = {
            "fixed_size": fixed.chunk(text),
            "by_sentences": sentence.chunk(text),
            "recursive": recursive.chunk(text),
     }

        comparison = {}
        for strategy, chunks in results.items():
            comparison[strategy] = {
                "count": len(chunks),
                "avg_length": (
                    sum(len(c) for c in chunks) / len(chunks)
                    if chunks else 0
                ),
                "chunks": chunks,
            }

        return comparison
        raise NotImplementedError("Implement ChunkingStrategyComparator.compare")
