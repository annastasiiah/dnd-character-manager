import pytest
from pydantic import ValidationError

from schemas.background import CharacterBackgroundUpdate
from schemas.character import CharacterUpdate
from schemas.character_class import CharacterClassUpdate
from schemas.race import RaceUpdate
from schemas.spell import SpellUpdate
from schemas.user import UserSelfUpdate, UserUpdate


@pytest.mark.parametrize(
    ("schema", "field"),
    [
        (CharacterUpdate, "name"),
        (CharacterUpdate, "strength"),
        (CharacterUpdate, "race_id"),
        (CharacterBackgroundUpdate, "name"),
        (CharacterClassUpdate, "name"),
        (RaceUpdate, "name"),
        (RaceUpdate, "description"),
        (RaceUpdate, "speed"),
        (SpellUpdate, "name"),
        (SpellUpdate, "level"),
        (SpellUpdate, "school"),
        (SpellUpdate, "casting_time"),
        (SpellUpdate, "spell_range"),
        (SpellUpdate, "duration"),
        (SpellUpdate, "description"),
        (UserUpdate, "email"),
        (UserUpdate, "nickname"),
        (UserUpdate, "role"),
        (UserUpdate, "password"),
        (UserSelfUpdate, "email"),
        (UserSelfUpdate, "nickname"),
        (UserSelfUpdate, "password"),
    ],
)
def test_patch_schema_rejects_null_for_non_nullable_fields(schema, field):
    with pytest.raises(ValidationError, match="Fields cannot be null"):
        schema.model_validate({field: None})


@pytest.mark.parametrize(
    ("schema", "payload"),
    [
        (CharacterBackgroundUpdate, {"description": None}),
        (CharacterBackgroundUpdate, {"skill_proficiencies": None}),
        (CharacterClassUpdate, {"description": None}),
        (CharacterClassUpdate, {"primary_ability": None}),
        (CharacterClassUpdate, {"hit_die": None}),
    ],
)
def test_patch_schema_allows_null_for_nullable_fields(schema, payload):
    result = schema.model_validate(payload)

    assert result.model_dump(exclude_unset=True) == payload


def test_user_self_update_allows_null_current_password_when_not_changing_password():
    result = UserSelfUpdate.model_validate({"current_password": None})

    assert result.model_dump(exclude_unset=True) == {"current_password": None}
