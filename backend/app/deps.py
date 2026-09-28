"""Shared dependencies that endpoints ask for.

FastAPI "dependency injection" is roughly Rails' `before_action`: an endpoint
declares a parameter such as `user: CurrentUser`, and FastAPI runs
`get_current_user` first and passes in the result.

`Annotated[User, Depends(get_current_user)]` means "a User, obtained by calling
get_current_user". The aliases below save repeating that in every endpoint.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession) -> User:
    """Rails: `current_user` in ApplicationController.

    Placeholder until auth exists: this is a single-user app, so we use the
    first user and create it the first time it's needed. Every query is still
    scoped by user_id, so adding real login later won't change the endpoints.
    """
    user = db.scalars(select(User).order_by(User.id).limit(1)).first()
    if user is None:
        user = User(name="Me")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
