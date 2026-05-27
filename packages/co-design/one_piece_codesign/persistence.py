"""SQLite persistence for co-design run history and graph snapshots."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


def connect_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS co_design_runs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            actor_mode TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            summary TEXT,
            goal_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS co_design_iterations (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            idx INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            objective_score REAL NOT NULL,
            summary TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS graph_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            iteration_id TEXT,
            snapshot_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def store_run(conn: sqlite3.Connection, run: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO co_design_runs
        (id, status, actor_mode, started_at, completed_at, summary, goal_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run["id"],
            run["status"],
            run["actorMode"],
            run["startedAt"],
            run.get("completedAt"),
            run.get("latestSummary"),
            json.dumps(run["goal"], sort_keys=True),
        ),
    )
    conn.commit()


def store_iteration(conn: sqlite3.Connection, run_id: str, iteration: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO co_design_iterations
        (id, run_id, idx, started_at, completed_at, objective_score, summary, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            iteration["id"],
            run_id,
            iteration["index"],
            iteration["startedAt"],
            iteration.get("completedAt"),
            iteration["objectiveScore"],
            iteration["summary"],
            json.dumps(iteration, sort_keys=True),
        ),
    )
    conn.commit()


def store_graph_snapshot(
    conn: sqlite3.Connection,
    run_id: str,
    snapshot: dict[str, Any],
    *,
    created_at: str,
    iteration_id: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO graph_snapshots (run_id, iteration_id, snapshot_json, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            run_id,
            iteration_id,
            json.dumps(snapshot, sort_keys=True),
            created_at,
        ),
    )
    conn.commit()
