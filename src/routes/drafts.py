from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List
from datetime import datetime

from src.models.db_schemas.Post import Post
from src.models.PostModel import PostModel
from src.models.enums.PostEnums import PostStatus
from src.models.schemas.DraftSChemas import (
    PostResponse,
    CreatePostRequest,
    EditPostRequest,
    EditPostResponse,
    ApproveDraftResponse,
    ApproveDraftRequest,
    RejectDraftRequest,
    RejectDraftResponse
)
from ..models.enums.ResponseSignal import ResponseSignal
from bson import ObjectId
# Router initialization
draft_router = APIRouter(
    prefix="/drafts",
    tags=["Draft drafts"]
)


async def get_post_model(request: Request) -> PostModel:
    """
    Dependency to get a PostModel instance from the app's database client.
    """
    db_client = request.app.db_client
    return await PostModel.create_instance(db_client)


# --------------------------
# Draft Management Endpoints
# --------------------------

@draft_router.post("/create_draft", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    req: CreatePostRequest,
    post_model: PostModel = Depends(get_post_model)
)-> PostResponse:
    """
    Create a new draft post.

    Args:
        req (CreatePostRequest): The request body containing title and content.
        post_model (PostModel): Database access layer.

    Returns:
        PostResponse: The created draft post.

    Raises:
        HTTPException 400: If post validation fails.
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
        created = await post_model.create_post(post)
        return PostResponse(**created.dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post validation failed: {str(e)}"
        )


@draft_router.get("/get_all_drafts", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def get_all_drafts(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    post_model: PostModel = Depends(get_post_model)
)-> List[PostResponse]:
    """
    Fetch all draft posts.

    Args:
        limit (int): Max number of posts to fetch (default=10, max=100).
        skip (int): Number of posts to skip (for pagination).
        post_model (PostModel): Database access layer.

    Returns:
        List[PostResponse]: List of draft posts.

    Raises:
        HTTPException 404: If no drafts are found.
    """
    posts = await post_model.list_draft_posts_by_user_id(limit=limit, skip=skip, user_id=user_id)

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)

    return [PostResponse(**p.dict()) for p in posts]

@draft_router.get("/get_all_accepted_posts", response_model=List[PostResponse], status_code=status.HTTP_200_OK )
async def get_all_accepted_posts(
    user_id:str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of posts to return (default=10, max=100)"),
    skip: int = Query(0, ge=0, description="Number of posts to skip for pagination"),
    post_model: PostModel = Depends(get_post_model)
)-> List[PostResponse]:
    """
        Retrieve all posts with status **ACCEPTED**.

        Args:
            limit (int): Maximum number of posts to fetch (default=10, max=100).
            skip (int): Number of posts to skip (used for pagination).
            post_model (PostModel): Database access layer dependency.

        Returns:
            List[PostResponse]: A list of accepted posts.

        Raises:
            HTTPException 404: If no accepted posts are found.
        """
    posts = await post_model.list_accepted_posts_by_user_id(user_id=user_id, limit=limit, skip=skip)

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.ACCEPTED_POST_NOT_FOUND.value)

    return [PostResponse(**p.dict()) for p in posts]


@draft_router.get("/get_all_rejected", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def get_all_rejected_posts(
    user_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of posts to return (default=10, max=100)"),
    skip: int = Query(0, ge=0, description="Number of posts to skip for pagination"),
    post_model: PostModel = Depends(get_post_model)
)-> List[PostResponse]:
    """
    Retrieve all posts with status **REJECTED**.

    Args:
        limit (int): Maximum number of posts to fetch (default=10, max=100).
        skip (int): Number of posts to skip (used for pagination).
        post_model (PostModel): Database access layer dependency.

    Returns:
        List[PostResponse]: A list of rejected posts.

    Raises:
        HTTPException 404: If no rejected posts are found.
    """
    posts = await post_model.list_rejected_posts_by_user_id(user_id=user_id, limit=limit, skip=skip)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.REJECTED_POST_NOT_FOUND.value)

    return [PostResponse(**p.dict()) for p in posts]


@draft_router.get("/get_one_draft", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_one_draft(
    Post_id: str = Query(..., description="Post ID in MongoDB"),
    post_model: PostModel = Depends(get_post_model)
)-> PostResponse:
    """
    Fetch a single draft by ID.

    Args:
        Post_id (str): The MongoDB ObjectId of the post.
    
    Returns:
        PostResponse: The requested draft post.

    Raises:
        HTTPException 404: If draft not found or status is not DRAFT.
    """
    post = await post_model.get_post_by_id(Post_id)
    if not post or post.status != PostStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
    return PostResponse(**post.dict())


@draft_router.put("/edit_draft", response_model=EditPostResponse, status_code=status.HTTP_200_OK)
async def edit_draft(
    req: EditPostRequest,
    post_model: PostModel = Depends(get_post_model)
)-> EditPostResponse:
    """
    Edit an existing draft's title or content.

    Args:
        req (EditPostRequest): Request body with post_id, new_title, new_content.
    
    Returns:
        EditPostResponse: Updated draft info.

    Raises:
        HTTPException 404: If post is not found.
    """
    updated_post = await post_model.update_post_by_id(req.post_id, req.new_content, req.new_title)
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)

    return EditPostResponse(id=str(updated_post.id), title=updated_post.title, content=updated_post.content)


@draft_router.put("/accept_draft", response_model=ApproveDraftResponse, status_code=status.HTTP_200_OK)
async def approve_draft(
    req: ApproveDraftRequest,
    post_model: PostModel = Depends(get_post_model)
)-> ApproveDraftResponse:
    """
    Approve a draft (change status to ACCEPTED).

    Args:
        req (ApproveDraftRequest): Request body with post_id.

    Returns:
        ApproveDraftResponse: Approved post ID and new status.

    Raises:
        HTTPException 404: If draft is not found.
    """
    post = await post_model.accept_draft_by_id(req.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
    return ApproveDraftResponse(id=str(req.post_id), status=PostStatus.ACCEPTED)


@draft_router.put("/reject_draft", response_model=RejectDraftResponse, status_code=status.HTTP_200_OK)
async def reject_draft(
    req: RejectDraftRequest,
    post_model: PostModel = Depends(get_post_model)
)-> RejectDraftResponse:
    """
    Reject a draft (change status to REJECTED).

    Args:
        req (RejectDraftRequest): Request body with post_id.

    Returns:
        RejectDraftResponse: Rejected post ID and new status.

    Raises:
        HTTPException 404: If draft is not found.
    """
    post = await post_model.reject_draft_by_id(req.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignal.DRAFT_NOT_FOUND.value)
    return RejectDraftResponse(id=str(req.post_id), status=PostStatus.REJECTED)