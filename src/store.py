from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401
            # TODO: initialize chromadb client + collection
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # TODO: build a normalized stored record for one document
        return {
        "id": doc.id,
        "content": doc.content,
        "metadata": doc.metadata,
        "embedding": self._embedding_fn(doc.content),
    }
        #raise NotImplementedError("Implement EmbeddingStore._make_record")

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # TODO: run in-memory similarity search over provided records
        query_embedding = self._embedding_fn(query)
        results = []
        for record in records:
         score = _dot(query_embedding, record["embedding"])

        results.append({
            "id": record["id"],
            "content": record["content"],
            "metadata": record["metadata"],
            "score": score,
        })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
        #raise NotImplementedError("Implement EmbeddingStore._search_records")

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # TODO: embed each doc and add to store
        records = []

        for doc in docs:
            record = self._make_record(doc)
            self._next_index += 1
            records.append(record)

        if self._use_chroma and self._collection:
            self._collection.add(
                ids=[r["id"] for r in records],
                documents=[r["content"] for r in records],
                embeddings=[r["embedding"] for r in records],
                metadatas=[r["metadata"] for r in records],
            )
        else:
            self._store.extend(records)
        #raise NotImplementedError("Implement EmbeddingStore.add_documents")

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # TODO: embed query, compute similarities, return top_k
        if self._use_chroma and self._collection:
            query_embedding = self._embedding_fn(query)

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            output = []
            for i in range(len(results["ids"][0])):
                output.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                })

            return output

        return self._search_records(query, self._store, top_k)
       # raise NotImplementedError("Implement EmbeddingStore.search")

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        # TODO
        if self._use_chroma and self._collection:
            return self._collection.count()
        return len(self._store)
        #raise NotImplementedError("Implement EmbeddingStore.get_collection_size")

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # TODO: filter by metadata, then search among filtered chunks
        if metadata_filter is None:
         return self.search(query, top_k)

        filtered = []

        for record in self._store:
         metadata = record.get("metadata", {})
        matched = all(
            metadata.get(key) == value
            for key, value in metadata_filter.items()
        )

        if matched:
            filtered.append(record)

        return self._search_records(query, filtered, top_k)
        #raise NotImplementedError("Implement EmbeddingStore.search_with_filter")

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        # TODO: remove all stored chunks where metadata['doc_id'] == doc_id
        original_size = len(self._store)

        self._store = [
          record for record in self._store
          if record["id"] != doc_id
        ]
        return len(self._store) < original_size
        #raise NotImplementedError("Implement EmbeddingStore.delete_document")
