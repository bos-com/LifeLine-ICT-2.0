
"""Duplicate detection for sensor observations.

This module identifies repeated observations without deleting or modifying
the original records.
"""

from collections.abc import Mapping, Sequence
from typing import Any


def find_duplicate_observations(
    observations: Sequence[Mapping[str, Any]],
    *,
    identity_fields: tuple[str, ...] = (
        "sensor_id",
        "timestamp",
    ),
) -> dict[str, Any]:
    """Identify duplicate observations using configured identity fields.

    Two observations are considered duplicates when all configured identity
    fields have equal, non-empty values.

    The first occurrence is retained as the original. Later occurrences are
    reported as duplicates. Input records are not modified.

    Args:
        observations: Sequence of observation mappings.
        identity_fields: Fields used to identify the same observation.

    Returns:
        A dictionary containing unique observations, duplicate records,
        and summary counts.

    Raises:
        TypeError: If observations or identity_fields have invalid types.
        ValueError: If identity_fields is empty or contains invalid names.
    """
    if isinstance(observations, (str, bytes)) or not isinstance(
        observations, Sequence
    ):
        raise TypeError("observations must be a sequence of mappings")

    if not isinstance(identity_fields, tuple):
        raise TypeError("identity_fields must be a tuple of field names")

    if not identity_fields:
        raise ValueError("identity_fields must not be empty")

    if any(
        not isinstance(field, str) or not field.strip()
        for field in identity_fields
    ):
        raise ValueError("identity field names must be non-empty strings")

    seen: set[tuple[Any, ...]] = set()
    unique_observations: list[Mapping[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            raise TypeError(
                f"observation at index {index} must be a mapping"
            )

        values = tuple(observation.get(field) for field in identity_fields)

        # Missing or blank identity values cannot safely establish identity.
        if any(
            value is None
            or (isinstance(value, str) and not value.strip())
            for value in values
        ):
            unique_observations.append(observation)
            continue

        try:
            key = values
            hash(key)
        except TypeError as exc:
            raise ValueError(
                f"identity fields at index {index} must be hashable"
            ) from exc

        if key in seen:
            duplicates.append(
                {
                    "index": index,
                    "identity": dict(zip(identity_fields, values)),
                    "observation": observation,
                }
            )
        else:
            seen.add(key)
            unique_observations.append(observation)

    return {
        "unique_observations": unique_observations,
        "duplicates": duplicates,
        "input_count": len(observations),
        "unique_count": len(unique_observations),
        "duplicate_count": len(duplicates),
    }
