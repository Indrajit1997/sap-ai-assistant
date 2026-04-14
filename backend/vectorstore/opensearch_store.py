from __future__ import annotations

import json

import structlog

from backend.config import get_settings
from backend.vectorstore.base import SearchResult, VectorStoreBase

log = structlog.get_logger()


class OpenSearchVectorStore(VectorStoreBase):
    """AWS OpenSearch-backed vector store for production deployment."""

    def __init__(self):
        from opensearchpy import OpenSearch, RequestsHttpConnection
        from requests_aws4auth import AWS4Auth
        import boto3

        settings = get_settings()
        credentials = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
            region_name=settings.aws_region,
        ).get_credentials()

        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            settings.aws_region,
            "aoss",  # OpenSearch Serverless
            session_token=credentials.token,
        )

        self._client = OpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )
        self._index = settings.opensearch_index
        self._ensure_index()
        log.info("opensearch_initialized", host=settings.opensearch_host, index=self._index)

    def _ensure_index(self):
        if not self._client.indices.exists(index=self._index):
            body = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100,
                    }
                },
                "mappings": {
                    "properties": {
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 384,  # all-MiniLM-L6-v2 dimension
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib",
                            },
                        },
                        "content": {"type": "text"},
                        "metadata": {"type": "object", "enabled": True},
                    }
                },
            }
            self._client.indices.create(index=self._index, body=body)
            log.info("opensearch_index_created", index=self._index)

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict] | None = None,
    ) -> None:
        # Bulk index
        bulk_body = []
        for i, doc_id in enumerate(ids):
            bulk_body.append(json.dumps({"index": {"_index": self._index, "_id": doc_id}}))
            doc = {
                "embedding": embeddings[i],
                "content": documents[i],
                "metadata": metadatas[i] if metadatas else {},
            }
            bulk_body.append(json.dumps(doc))

        body = "\n".join(bulk_body) + "\n"
        self._client.bulk(body=body)
        self._client.indices.refresh(index=self._index)
        log.info("opensearch_added", count=len(ids))

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        query = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k,
                    }
                }
            },
            "_source": ["content", "metadata"],
        }

        response = self._client.search(index=self._index, body=query)
        results = []
        for hit in response["hits"]["hits"]:
            results.append(SearchResult(
                id=hit["_id"],
                content=hit["_source"]["content"],
                score=hit["_score"],
                metadata=hit["_source"].get("metadata", {}),
            ))
        return results

    def delete(self, ids: list[str]) -> None:
        bulk_body = []
        for doc_id in ids:
            bulk_body.append(json.dumps({"delete": {"_index": self._index, "_id": doc_id}}))
        body = "\n".join(bulk_body) + "\n"
        self._client.bulk(body=body)
        log.info("opensearch_deleted", count=len(ids))

    def count(self) -> int:
        response = self._client.count(index=self._index)
        return response["count"]
