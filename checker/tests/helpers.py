"""Shared fixtures for checker tests."""

import copy
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_repo_json(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def results():
    return copy.deepcopy(load_repo_json("results/results.json"))


def rule_ids(findings):
    return sorted({f.rule_id for f in findings})
