from app.schemas.profile import ProfileResponse, ProfileUpsertRequest


class InMemoryProfileStore:
    def __init__(self) -> None:
        self._profiles: dict[str, ProfileResponse] = {}

    def get_profile(self, user_id: str) -> ProfileResponse | None:
        return self._profiles.get(user_id)

    def upsert_profile(
        self,
        user_id: str,
        request: ProfileUpsertRequest,
    ) -> ProfileResponse:
        profile = ProfileResponse(id=user_id, exists=True, **request.model_dump())
        self._profiles[user_id] = profile
        return profile
