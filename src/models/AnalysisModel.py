#the code of Analysis model
from .BaseModel import BaseModel
from .db_schemas.Analysis import Analysis
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime
from .enums.DBEnums import DBEnums
from .enums.AnalysisEnums import AnlaysisType

class AnalysisModel(BaseModel):
    def __init__(self, db_client):
        """
        Initialize the AnalysisModel with a database client.

        Args:
            db_client (object): The database client instance for MongoDB operations.
        """
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_ANALYTICS_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client: object) -> "AnalysisModel":
        """
        Asynchronously create and initialize an instance of AnalysisModel.

        This method ensures the required collection and indexes are set up before returning the instance.

        Args:
            db_client (object): The database client instance for MongoDB operations.

        Returns:
            AnalysisModel: An initialized instance of AnalysisModel.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self) -> None:
        """
        Initialize the analytics collection in the database.

        Checks if the analytics collection exists; if not, creates it and sets up the necessary indexes
        as defined in the Analysis schema.
        """
        all_collections = await self.db.list_collection_names()
        if DBEnums.COLLECTION_ANALYTICS_NAME.value not in all_collections:
            self.collection = self.db[DBEnums.COLLECTION_ANALYTICS_NAME.value]
            indexes = Analysis.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )
    
    async def create_analysis(self, analysis: Analysis) -> Analysis:
        """
        Insert a new analysis document into the analytics collection.

        Args:
            analysis (Analysis): The Analysis object to be inserted.

        Returns:
            Analysis: The inserted Analysis object with its MongoDB ID set.
        """
        result = await self.collection.insert_one(analysis.dict(by_alias=True, exclude_unset=True))
        return result.inserted_id
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Analysis]:
        """
        Retrieve a single analysis document by its unique ID.

        Args:
            analysis_id (str): The string representation of the analysis document's ObjectId.

        Returns:
            Optional[Analysis]: The Analysis object if found, otherwise None.
        """
        result = await self.collection.find(
            {
                "_id": ObjectId(analysis_id)
            }
        )
        
        return Analysis(**result) if result else None
    
    async def get_all_analyses_by_user_id(self, user_id: ObjectId) -> List[Analysis]:
        """
        Retrieve all analysis documents associated with a specific user ID.

        Args:
            user_id (ObjectId): The ObjectId of the post to filter analyses by.

        Returns:
            List[Analysis]: A list of Analysis objects linked to the given post.
        """
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        analyses = []
        async for doc in cursor:
            analyses.append(Analysis(**doc))
        return analyses

    async def delete_analysis_by_id(self, analysis_id: ObjectId) -> bool:
        """
        Delete an analysis document by its unique ID.

        Args:
            analysis_id (ObjectId): The ObjectId of the analysis document to delete.

        Returns:
            bool: True if a document was deleted, False otherwise.
        """
        result = await self.collection.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count > 0

    async def list_analyses(self, limit: int = 10, skip: int = 0) -> List[Analysis]:
        """
        List analysis documents with pagination support.

        Args:
            limit (int, optional): The maximum number of documents to return. Defaults to 10.
            skip (int, optional): The number of documents to skip. Defaults to 0.

        Returns:
            List[Analysis]: A list of Analysis objects within the specified range.
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        analyses = []
        async for doc in cursor:
            analyses.append(Analysis(**doc))
        return analyses
    
    async def get_interaction_analysis_by_user_id(self, user_id: str, skip: int, limit: int) -> List[Analysis]:
        """
        Retrieve all INTERACTION_ANALYSIS documents associated with a specific user.

        Args:
            user_id (ObjectId): The ObjectId of the user to filter analyses by.

        Returns:
            List[Analysis]: A list of Analysis objects where analysisType is INTERACTION_ANALYSIS
                            and linked to the given user.
        """
        cursor = self.collection.find({
            "user_id": user_id,
            "analysisType": AnlaysisType.INTERACTION_ANALYSIS
        }).skip(skip).limit(limit)
        analyses = []
        async for doc in cursor:
            analyses.append(Analysis(**doc))
        return analyses

    async def get_competitor_analysis_by_user_id(self, user_id: str, skip, limit) -> List[Analysis]:
        """
        Retrieve all COMPETITOR_ANALYSIS documents associated with a specific user.

        Args:
            user_id (ObjectId): The ObjectId of the user to filter analyses by.

        Returns:
            List[Analysis]: A list of Analysis objects where analysisType is COMPETITOR_ANALYSIS
                            and linked to the given user.
        """
        cursor = self.collection.find({
            "user_id": user_id,
            "analysisType": AnlaysisType.COMPETITOR_ANALYSIS
        }).skip(skip).limit(limit)
        analyses = []
        async for doc in cursor:
            analyses.append(Analysis(**doc))
        return analyses
