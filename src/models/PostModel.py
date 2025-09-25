# Posts model
from .BaseModel import BaseModel
from .db_schemas.Post import Post
from .enums.DBEnums import DBEnums
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime


class PostModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DBEnums.COLLECTION_POST_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self) -> None:
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_POST_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnums.COLLECTION_POST_NAME.value]
            indexes = Post.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                    sparse=index.get("sparse", False)
                )
    
    async def create_post(self, post: Post) -> Post:
        result = await self.collection.insert_one(post.dict(by_alias=True, exclude_unset=True))
        post.id = result.id
        return post
    
    async def get_post_by_id(self, post_id: str) -> Optional[Post]:
        result = await self.collection.find_one({
            "id": ObjectId(post_id)
        })
        
        return Post(**result) if result else None
    
    
    async def update_post_by_id(self, post_id: str, new_post_content: str) -> Optional[str]:
        """Update post content by ID and set updatedcontent"""
        update_data = {
            "updated_content": new_post_content,
            "updatedAt": datetime.utcnow(),
        }
        
        result = await self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            updated_post = await self.get_post_by_id(post_id)
            return updated_post
        return None
    
    async def delete_post_by_id(self, post_id: str) -> bool:
        """Delete Post By ID"""
        result = await self.collection.delete_one(
            {"_id": ObjectId(post_id)}
        )
        return result.deleted_count > 0

    async def list_posts(self, limit: int = 10, skip: int = 0) -> List[Post]:
        """Retrieve list of posts with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        posts = []
        async for doc in cursor:
            posts.append(Post(**doc))
        return posts
    
