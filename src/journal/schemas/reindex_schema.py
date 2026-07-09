from pydantic import BaseModel, EmailStr


class ReindexRequest(BaseModel):
    user_email: EmailStr | None = None


class ReindexResponse(BaseModel):
    reindexed_count: int

