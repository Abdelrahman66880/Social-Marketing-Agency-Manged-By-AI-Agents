from fastapi import APIRouter, Depends, HTTPException, status, Request, Path
from typing import List
from datetime import datetime
from bson import ObjectId

from src.models.db_schemas.Post import Post
from src.models.PostModel import PostModel
from src.models.enums.PostEnums import PostStatus
from src.models.schemas.DraftSChemas import (
    CreatePostRequest,
    EditPostRequest,
    EditPostResponse,
    ApproveDraftResponse,
    RejectDraftResponse
)
from ..models.enums.ResponseSignal import ResponseSignal


# -----------------------------------
# Router Initialization
# -----------------------------------
draft_router = APIRouter(
    prefix="/drafts",
    tags=["Draft Management"]
)


# -----------------------------------
# Dependency Injection
# -----------------------------------
async def get_post_model(request: Request) -> PostModel:
    """
    Retrieve a `PostModel` instance for database operations.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        PostModel: An initialized PostModel instance connected to the database.
    """
    db_client = request.app.db_client
    return await PostModel.create_instance(db_client)


# -----------------------------------
# Draft Management Endpoints
# -----------------------------------

@draft_router.post(
    "/", 
    response_model=Post, 
    status_code=status.HTTP_201_CREATED
)
async def create_draft(
    req: CreatePostRequest,
    post_model: PostModel = Depends(get_post_model)
) -> Post:
    """
    Create a new draft post.

    Args:
        req (CreatePostRequest): Request body containing `title`, `content`, and `user_id`.
        post_model (PostModel): The database model dependency.

    Returns:
        Post: The newly created draft post.

    Raises:
        HTTPException(400): If the post validation fails.
    """
    try:
        post = Post(
            title=req.title,
            content=req.content,
            createdAt=datetime.utcnow(),
            status=PostStatus.DRAFT,
            userFeedback=0.0,
            comments=[],
            user_id= ObjectId(req.user_id)
        )
        res = await post_model.create_post(post)
        post.id = str(res)
        return post

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post validation failed: {str(e)}"
        )


@draft_router.get(
    "/users/{user_id}/{limit}/{skip}",
    response_model=List[Post],
    status_code=status.HTTP_200_OK
)
async def get_all_drafts(
    user_id: str,
    limit: int,
    skip: int,
    post_model: PostModel = Depends(get_post_model)
) -> List[Post]:
    """
    Retrieve all **draft** posts belonging to a specific user.

    Args:
        user_id (str): The user’s unique identifier.
        limit (int): The maximum number of drafts to fetch.
        skip (int): The number of drafts to skip (for pagination).
        post_model (PostModel): The database model dependency.

    Returns:
        List[Post]: A list of draft posts.

    Raises:
        HTTPException(404): If no drafts are found.
    """
    try: 
        posts = await post_model.list_draft_posts_by_user_id(limit=limit, skip=skip, user_id=user_id)
        if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
        return posts
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to get posts for the following reason: {str(e)}"
        )

@draft_router.get(
    "/users/{user_id}/accepted/{limit}/{skip}",
    response_model=List[Post],
    status_code=status.HTTP_200_OK
)
async def get_all_accepted_posts(
    user_id: str,
    limit: int,
    skip: int,
    post_model: PostModel = Depends(get_post_model)
) -> List[Post]:
    """
    Retrieve all **accepted** posts belonging to a specific user.

    Args:
        user_id (str): The user’s unique identifier.
        limit (int): The maximum number of posts to fetch.
        skip (int): The number of posts to skip (for pagination).
        post_model (PostModel): The database model dependency.

    Returns:
        List[Post]: A list of accepted posts.

    Raises:
        HTTPException(404): If no accepted posts are found.
    """
    try:
        posts = await post_model.list_accepted_posts_by_user_id(user_id=user_id, limit=limit, skip=skip)
        if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.ACCEPTED_POST_NOT_FOUND.value)
        return posts
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to get posts for the following reason: {str(e)}"
        )


@draft_router.get(
    "/users/{user_id}/rejected/{limit}/{skip}",
    response_model=List[Post],
    status_code=status.HTTP_200_OK
)
async def get_all_rejected_posts(
    user_id: str,
    limit: int,
    skip: int,
    post_model: PostModel = Depends(get_post_model)
) -> List[Post]:
    """
    Retrieve all **rejected** posts belonging to a specific user.

    Args:
        user_id (str): The user’s unique identifier.
        limit (int): The maximum number of posts to fetch.
        skip (int): The number of posts to skip (for pagination).
        post_model (PostModel): The database model dependency.

    Returns:
        List[Post]: A list of rejected posts.

    Raises:
        HTTPException(404): If no rejected posts are found.
    """
    try: 
        posts = await post_model.list_rejected_posts_by_user_id(user_id=user_id, limit=limit, skip=skip)
        if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.REJECTED_POST_NOT_FOUND.value)
        return posts
    
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to get posts for the following reason: {str(e)}"
        )


@draft_router.get(
    "/{draft_id}",
    response_model=Post,
    status_code=status.HTTP_200_OK
)
async def get_one_draft(
    draft_id: str,
    post_model: PostModel = Depends(get_post_model)
) -> Post:
    """
    Retrieve a single **draft** post by its unique ID.

    Args:
        draft_id (str): The MongoDB ObjectId of the draft post.
        post_model (PostModel): The database model dependency.

    Returns:
        Post: The requested draft post.

    Raises:
        HTTPException(404): If the draft is not found or its status is not DRAFT.
    """
    try:
        post = await post_model.get_post_by_id(draft_id)
        if not post or post.status != PostStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
        return post
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to get draft for the following reason: {str(e)}"
        )

@draft_router.put(
    "/{draft_id}",
    response_model=EditPostResponse,
    status_code=status.HTTP_200_OK
)
async def edit_draft(
    draft_id: str,
    req: EditPostRequest,
    post_model: PostModel = Depends(get_post_model)
) -> EditPostResponse:
    """
    Edit an existing draft post’s title and/or content.

    Args:
        draft_id (str): The unique ID of the draft post to edit.
        req (EditPostRequest): The updated title and/or content.
        post_model (PostModel): The database model dependency.

    Returns:
        EditPostResponse: The updated draft information.

    Raises:
        HTTPException(404): If the draft post is not found.
    """
    try:
        updated_post = await post_model.update_post_by_id(draft_id, req.new_content, req.new_title)
        if not updated_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)

        return EditPostResponse(id=str(updated_post.id), title=updated_post.title, content=updated_post.content)
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to edit for the following reason: {str(e)}"
        )


@draft_router.put(
    "/{draft_id}/accept",
    response_model=ApproveDraftResponse,
    status_code=status.HTTP_200_OK
)
async def approve_draft(
    draft_id: str,
    post_model: PostModel = Depends(get_post_model)
) -> ApproveDraftResponse:
    """
    Approve a draft post (change its status to **ACCEPTED**).

    Args:
        draft_id (str): The unique ID of the draft post.
        post_model (PostModel): The database model dependency.

    Returns:
        ApproveDraftResponse: The approved draft’s ID and new status.

    Raises:
        HTTPException(404): If the draft is not found.
    """
    try:
        post = await post_model.accept_draft_by_id(draft_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
        return ApproveDraftResponse(id=str(draft_id), status=PostStatus.ACCEPTED)
    
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to edit for the following reason: {str(e)}"
        )


@draft_router.put(
    "/{draft_id}/reject",
    response_model=RejectDraftResponse,
    status_code=status.HTTP_200_OK
)
async def reject_draft(
    draft_id: str,
    post_model: PostModel = Depends(get_post_model)
) -> RejectDraftResponse:
    """
    Reject a draft post (change its status to **REJECTED**).

    Args:
        draft_id (str): The unique ID of the draft post.
        post_model (PostModel): The database model dependency.

    Returns:
        RejectDraftResponse: The rejected draft’s ID and new status.

    Raises:
        HTTPException(404): If the draft is not found.
    """
    try:
        post = await post_model.reject_draft_by_id(draft_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
        return RejectDraftResponse(id=str(draft_id), status=PostStatus.REJECTED)
    
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to edit for the following reason: {str(e)}"
        )