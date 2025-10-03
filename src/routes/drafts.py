from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List
from datetime import datetime

from src.models.db_schemas.Post import Post
from src.models.PostModel import PostModel
from src.models.enums.UserEnums import PostStatus
from models.schemas.DraftSChemas import (
    PostResponse,
    CreatePostRequest,
    EditPostRequest,
    EditPostResponse,
    ApproveDraftResponse,
    ApproveDraftRequest,
    RejectDraftRequest,
    RejectDraftResponse
)


# Router initialization
content_router = APIRouter(
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

@content_router.post("/create_draft", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
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
            userRate=0.0,
            comments=[]
        )
        created = await post_model.create_post(post)
        return PostResponse(**created.dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post validation failed: {str(e)}"
        )


@content_router.get("/get_all_drafts", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def get_all_drafts(
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
    posts = await post_model.list_posts(limit=limit, skip=skip)
    drafts = [p for p in posts if p.status == PostStatus.DRAFT]

    if not drafts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No draft posts found")

    return [PostResponse(**p.dict()) for p in drafts]


async def get_all_accepted_posts(
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
    posts = await post_model.list_posts(limit=limit, skip=skip)
    accepted = [p for p in posts if p.status == PostStatus.ACCEPTED]

    if not accepted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No accepted posts found")

    return [PostResponse(**p.dict()) for p in accepted]


@content_router.get("/get_all_rejected", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def get_all_rejected_posts(
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
    posts = await post_model.list_posts(limit=limit, skip=skip)
    rejected = [p for p in posts if p.status == PostStatus.REJECTED]

    if not rejected:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rejected posts found")

    return [PostResponse(**p.dict()) for p in rejected]


@content_router.get("/get_one_draft", response_model=PostResponse, status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return PostResponse(**post.dict())


@content_router.put("/edit_draft", response_model=EditPostResponse, status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return EditPostResponse(id=str(updated_post.id), title=updated_post.title, content=updated_post.content)


@content_router.put("/accept_draft", response_model=ApproveDraftResponse, status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return ApproveDraftResponse(id=str(req.post_id), status=PostStatus.ACCEPTED)


@content_router.put("/reject_draft", response_model=RejectDraftResponse, status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return RejectDraftResponse(id=str(req.post_id), status=PostStatus.REJECTED)