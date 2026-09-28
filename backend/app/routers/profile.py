"""Rails equivalent: a singular `resource :profile` with show and update."""

from fastapi import APIRouter

from app.deps import CurrentUser, DbSession
from app.schemas import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


# `@router.get(...)` is a decorator: it registers the function below as the
# handler for GET /api/profile. Rails: `get "/profile", to: "profiles#show"`.
@router.get("", response_model=ProfileRead)
def show_profile(user: CurrentUser):
    return user


@router.put("", response_model=ProfileRead)
def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbSession):
    # Rails: `current_user.update!(profile_params)`
    for field, value in payload.model_dump().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
