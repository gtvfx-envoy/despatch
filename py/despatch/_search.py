"""Deterministic application search and ranking."""

from __future__ import annotations

import re

from . import _models


def rankApplications(
    applications: tuple[_models.ApplicationEntry, ...],
    query: str,
    favorites: frozenset[str] = frozenset(),
    recent_applications: tuple[str, ...] = (),
) -> tuple[_models.ApplicationEntry, ...]:
    """Return applications ordered by text relevance and user preference.

    Args:
        applications: Candidate application entries.
        query: User-entered search text.
        favorites: Stable identities currently favorited.
        recent_applications: Stable identities ordered from most recent.

    Returns:
        Matching applications in deterministic relevance order.

    """
    normalized_query = " ".join(query.casefold().split())
    if not normalized_query:
        return applications
    recent_rank = {stable_id: index for index, stable_id in enumerate(recent_applications)}
    ranked: list[tuple[tuple[int, int, int, str], _models.ApplicationEntry]] = []
    for application in applications:
        score = _scoreApplication(application, normalized_query)
        if score is None:
            continue
        preference = 0 if application.stable_id in favorites else 1
        history = recent_rank.get(application.stable_id, len(recent_rank) + 1)
        ranked.append(((score, preference, history, application.name.casefold()), application))
    ranked.sort(key=lambda result: result[0])
    return tuple(application for _, application in ranked)


def _scoreApplication(application: _models.ApplicationEntry, query: str) -> int | None:
    """Calculate a lower-is-better search score."""
    name = application.name.casefold()
    command = application.command.casefold()
    searchable_parts = [name, command, application.description.casefold()]
    searchable_parts.extend(value.casefold() for value in application.keywords)
    searchable = " ".join(searchable_parts)
    if name == query:
        return 0
    if name.startswith(query):
        return 10
    if any(word.startswith(query) for word in re.split(r"[^a-z0-9]+", name)):
        return 20
    if query in name:
        return 30
    if command == query:
        return 40
    if command.startswith(query):
        return 50
    if query in searchable:
        return 60
    if _isSubsequence(query, searchable):
        return 80
    return None


def _isSubsequence(query: str, text: str) -> bool:
    """Return whether query characters occur in order within text."""
    query_index = 0
    for character in text:
        if query_index < len(query) and character == query[query_index]:
            query_index += 1
            if query_index == len(query):
                return True
    return False
