#the code of Analysis model
from .BaseModel import BaseModel
from .db_schemas.Analysis import Analysis
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime
from .enums.DBEnums import DBEnums


class AnalysisModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client(DBEnums.COLLECTION_ANALYTICS_NAME.value)
        
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self) -> None:
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_ANALYSIS_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnums.COLLECTION_ANALYSIS_NAME.value]
            indexes = Analysis.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                    sparse=index.get("sparse", False),
                )
    
    async def create_analysis(self, analysis: Analysis) -> Analysis:
        result = await self.collection.inset_one(analysis.dict(by_alias=True, exclude_unset=True))
        analysis.id = result.inserted_id
        return analysis
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Analysis]:
        result = await self.collection.find(
            {
                "_id": ObjectId(analysis_id)
            }
        )
        
        return Analysis(**result) if result else None
    
    async def get_analyses_by_post_id(self, post_id: ObjectId) -> List[Analysis]:
        cursor = self.collection.find({"post_id": ObjectId(post_id)})
        analyses = []
        async for doc in cursor:
            analyses.append(Analysis(**doc))
        return analyses

    async def delete_analysis_by_id(self, analysis_id: ObjectId) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count > 0

    async def list_analyses(self, limit: int = 10, skip: int = 0) -> List[Analysis]:
        cursor = self.collection.find().skip(skip).limit(limit)
        analyses = []
        async for doc in cursor:
            analyses.append(Analysis(**doc))
        return analyses