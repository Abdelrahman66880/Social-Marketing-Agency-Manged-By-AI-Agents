# Posts model
from .BaseModel import BaseModel
from .db_schemas.Post import Post
from .enums.DBEnums import DBEnums
from .enums.UserEnums import PostStatus
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime


class PostModel(BaseModel):
    def __init__(self, db_client):
        """
        Initialize the PostModel with a MongoDB client.

        Args:
            db_client (object): The MongoDB client instance for database operations.
        """
        super().__init__(db_client)
        self.collection = self.db_client[DBEnums.COLLECTION_POST_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Asynchronously create and initialize a PostModel instance.

        Ensures the post collection and its indexes are set up before returning the instance.

        Args:
            db_client (object): The MongoDB client instance.

        Returns:
            PostModel: An initialized PostModel instance.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self) -> None:
        """
        Initialize the post collection in the database.

        Checks if the post collection exists; if not, creates it and sets up the necessary indexes
        as defined in the Post schema.
        """
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_POST_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnums.COLLECTION_POST_NAME.value]
            indexes = Post.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )
    
    async def create_post(self, post: Post) -> Post:
        """
        Insert a new post document into the post collection.

        Args:
            post (Post): The Post object to be inserted.

        Returns:
            Post: The inserted Post object with its MongoDB ID set.
        """
        result = await self.collection.insert_one(post.dict(by_alias=True, exclude_unset=True))
        post.id = result.inserted_id
        return post
    
    async def get_post_by_id(self, post_id: str) -> Optional[Post]:
        """
        Retrieve a single post document by its unique ID.

        Args:
            post_id (str): The string representation of the post's ObjectId.

        Returns:
            Optional[Post]: The Post object if found, otherwise None.
        """
        result = await self.collection.find_one({
            "_id": ObjectId(post_id)
        })
        return Post(**result) if result else None
    
    
    async def update_post_by_id(self, post_id: str, new_post_content: str, new_title: str) -> Post:
        """
        Update the content of a post by its unique ID.

        Args:
            post_id (str): The string representation of the post's ObjectId.
            new_post_content (str): The new content to update in the post.

        Returns:
            The updated Post object if the update was successful, otherwise None.
        """
        update_data = {
            "content": new_post_content,
            "title": new_title,
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
        """
        Delete a post document by its unique ID.

        Args:
            post_id (str): The string representation of the post's ObjectId.

        Returns:
            bool: True if a document was deleted, False otherwise.
        """
        result = await self.collection.delete_one(
            {"_id": ObjectId(post_id)}
        )
        return result.deleted_count > 0

    async def list_posts(self, limit: int = 10, skip: int = 0) -> List[Post]:
        """
        Retrieve a list of post documents with pagination support.

        Args:
            limit (int, optional): The maximum number of posts to return. Defaults to 10.
            skip (int, optional): The number of posts to skip. Defaults to 0.

        Returns:
            List[Post]: A list of Post objects within the specified range.
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        posts = []
        async for doc in cursor:
            posts.append(Post(**doc))
        return posts

    async def accept_draft_by_id(self, post_id: str) -> bool:
            """
            Change the status of the draft to ACCEPTED.

            Args:
                post_id (str): The string representation of the post's ObjectId.

            Returns:
                bool: true if found false if not found
            """
            result = await self.collection.update_one(
                {"_id": ObjectId(post_id), "status": PostStatus.DRAFT},  # only update if it's a draft
                {"$set": {"status": PostStatus.ACCEPTED}}
            )

            if result.modified_count > 0:
                # fetch the updated post
                return True
            return False
    

    async def reject_draft_by_id(self, post_id: str) -> bool:
            """
            Change the status of the draft to REJECTED.

            Args:
                post_id (str): The string representation of the post's ObjectId.

            Returns:
                bool: true if found false if not found
            """
            result = await self.collection.update_one(
                {"_id": ObjectId(post_id), "status": PostStatus.DRAFT},  # only update if it's a draft
                {"$set": {"status": PostStatus.REJECTED}}
            )

            if result.modified_count > 0:
                # fetch the updated post
                return True
            return False