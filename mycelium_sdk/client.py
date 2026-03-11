from __future__ import annotations

from typing import Any

import httpx


class MyceliumClient:
    """
    Python SDK for the Mycelium API.

    Usage:
        client = MyceliumClient(api_url="http://localhost:8000", api_key="mk_...")
        results = client.seek(goal="...", scope="task", context={}, tags=[])
        ph_id   = client.publish(goal="...", path={}, tags=[])
        client.feedback(ph_id, result="success", source="agent")
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: str = "",
        timeout: float = 30.0,
        agent_id: str | None = None,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.agent_id = agent_id
        self._headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    # ─── seek ─────────────────────────────────────────────────────────────────

    def seek(
        self,
        goal: str,
        scope: str = "task",
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Query the Mycelium platform for matching pheromones.

        Returns a list of match dicts, sorted by rank_score (similarity × strength).
        """
        payload = {
            "fingerprint": {
                "goal": goal,
                "scope": scope,
                "context": context or {},
                "tags": tags or [],
            },
            "limit": limit,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.api_url}/pheromones/match",
                json=payload,
                headers=self._headers,
            )
            resp.raise_for_status()
        return resp.json()["matches"]

    # ─── publish ──────────────────────────────────────────────────────────────

    def publish(
        self,
        goal: str,
        path: dict[str, Any],
        scope: str = "task",
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        publisher_handle: str | None = None,
    ) -> str:
        """
        Publish a new pheromone (execution path) to the platform.

        Returns the pheromone ID.
        """
        payload = {
            "fingerprint": {
                "goal": goal,
                "scope": scope,
                "context": context or {},
                "tags": tags or [],
            },
            "path": path,
            "publisher_agent_id": self.agent_id,
            "publisher_handle": publisher_handle,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.api_url}/pheromones",
                json=payload,
                headers=self._headers,
            )
            resp.raise_for_status()
        return resp.json()["id"]

    # ─── feedback ─────────────────────────────────────────────────────────────

    def feedback(
        self,
        pheromone_id: str,
        result: str,
        source: str = "agent",
    ) -> dict[str, Any]:
        """
        Submit strength feedback for a pheromone.

        result: "success" | "fail" | "unknown"
        source: "agent" | "user"

        Returns the API response dict with updated strength.
        """
        if result not in ("success", "fail", "unknown"):
            raise ValueError(f"result must be 'success', 'fail', or 'unknown', got: {result!r}")
        if source not in ("agent", "user"):
            raise ValueError(f"source must be 'agent' or 'user', got: {source!r}")

        payload: dict[str, Any] = {
            "result": result,
            "source": source,
        }
        if self.agent_id:
            payload["agent_id"] = self.agent_id

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.api_url}/pheromones/{pheromone_id}/feedback",
                json=payload,
                headers=self._headers,
            )
            resp.raise_for_status()
        return resp.json()

    # ─── list ─────────────────────────────────────────────────────────────────

    def list_pheromones(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List pheromones ordered by strength (descending)."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                f"{self.api_url}/pheromones",
                params={"limit": limit, "offset": offset},
                headers=self._headers,
            )
            resp.raise_for_status()
        return resp.json()
