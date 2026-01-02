import pickle
from typing import Any, AsyncIterator, Dict, Optional, Sequence
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langchain_core.runnables import RunnableConfig

class AsyncMongoDBSaver(BaseCheckpointSaver):
    """
    A persistent checkpoint saver using MongoDB (via Motor).
    """
    client: AsyncIOMotorClient
    db_name: str
    collection_name: str

    def __init__(self, client: AsyncIOMotorClient, db_name: str = "agent_memory", collection_name: str = "checkpoints"):
        super().__init__()
        self.client = client
        self.db_name = db_name
        self.collection_name = collection_name
        self.collection = self.client[self.db_name][self.collection_name]

    @classmethod
    @asynccontextmanager
    async def from_conn_string(cls, conn_string: str) -> AsyncIterator["AsyncMongoDBSaver"]:
        client = AsyncIOMotorClient(conn_string)
        try:
            yield cls(client)
        finally:
            client.close()

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        # Find latest checkpoint for thread
        query = {"thread_id": thread_id}
        
        # We need to sort by thread_ts descending
        doc = await self.collection.find_one(query, sort=[("thread_ts", -1)])
        
        if not doc:
            return None
            
        # Deserialize
        checkpoint = pickle.loads(doc["checkpoint"])
        metadata = pickle.loads(doc["metadata"])
        
        # Usually LangGraph also needs parent config (not implemented deep here for simplicity)
        return CheckpointTuple(config, checkpoint, metadata, None)

    async def asearch(
        self,
        metadata_filter: Dict[str, Any],
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        # Implementation skipped for MVP
        pass

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Dict[str, Any],
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        
        doc = {
            "thread_id": thread_id,
            "thread_ts": checkpoint["id"], # ID is usually timestamp
            "checkpoint": pickle.dumps(checkpoint),
            "metadata": pickle.dumps(metadata)
        }
        
        await self.collection.update_one(
            {"thread_id": thread_id, "thread_ts": checkpoint["id"]},
            {"$set": doc},
            upsert=True
        )
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "thread_ts": checkpoint["id"],
            }
        }
