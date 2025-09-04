"""
Notes CRUD routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user
from ..core.database import get_db_session
from ..models.models import Note, User
from ..schemas.schemas import NoteCreate, NoteUpdate, NoteOut

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post(
    "",
    response_model=NoteOut,
    summary="Create a note",
    description="Create a new note for the authenticated user.",
    status_code=201,
)
# PUBLIC_INTERFACE
async def create_note(
    payload: NoteCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    """Create a new note for the current user."""
    note = Note(title=payload.title, content=payload.content or "", owner_id=current_user.id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get(
    "",
    response_model=List[NoteOut],
    summary="List notes",
    description="List all notes belonging to the authenticated user.",
)
# PUBLIC_INTERFACE
async def list_notes(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[NoteOut]:
    """List all notes for the current user."""
    result = await db.scalars(select(Note).where(Note.owner_id == current_user.id).order_by(Note.created_at.desc()))
    return list(result.all())


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note",
    description="Get a specific note by its ID if it belongs to the authenticated user.",
    responses={404: {"description": "Note not found"}},
)
# PUBLIC_INTERFACE
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    """Retrieve a note by ID for the current user."""
    note = await db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == current_user.id))
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Update a note's title or content for the authenticated user.",
    responses={404: {"description": "Note not found"}},
)
# PUBLIC_INTERFACE
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    """Update fields of a note, returning the updated entity."""
    note = await db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == current_user.id))
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    await db.commit()
    await db.refresh(note)
    return note


@router.delete(
    "/{note_id}",
    summary="Delete a note",
    description="Delete a specific note belonging to the authenticated user.",
    responses={204: {"description": "Deleted successfully"}, 404: {"description": "Note not found"}},
    status_code=204,
)
# PUBLIC_INTERFACE
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a note by ID if it belongs to the current user."""
    note = await db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == current_user.id))
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await db.delete(note)
    await db.commit()
    return None
