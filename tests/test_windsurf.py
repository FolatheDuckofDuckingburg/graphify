import json
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from graphify.platforms.windsurf import WindsurfIntegrator, _WINDSURF_RULES
import graphify.__main__ as m


def test_windsurf_install_new(tmp_path):
    integrator = WindsurfIntegrator(project_root=tmp_path)
    assert integrator.install() is True

    config_file = tmp_path / ".codeium" / "config.json"
    assert config_file.exists()

    data = json.loads(config_file.read_text(encoding="utf-8"))
    assert data["version"] == "1.0"
    assert "agent" in data

    agent = data["agent"]
    assert len(agent["rules"]) == len(_WINDSURF_RULES)
    for r in _WINDSURF_RULES:
        assert r in agent["rules"]

    target_path = str(Path(tmp_path).resolve() / "graphify-out" / "graph.json")
    assert target_path in agent["context_paths"]


def test_windsurf_install_existing_valid(tmp_path):
    config_dir = tmp_path / ".codeium"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"

    initial_config = {
        "version": "1.0",
        "custom_key": "custom_value",
        "agent": {
            "rules": ["Custom user rule."],
            "context_paths": ["/some/other/path/graph.json"]
        }
    }
    config_file.write_text(json.dumps(initial_config), encoding="utf-8")

    integrator = WindsurfIntegrator(project_root=tmp_path)
    assert integrator.install() is True

    data = json.loads(config_file.read_text(encoding="utf-8"))
    assert data["custom_key"] == "custom_value"

    agent = data["agent"]
    assert "Custom user rule." in agent["rules"]
    for r in _WINDSURF_RULES:
        assert r in agent["rules"]

    assert "/some/other/path/graph.json" in agent["context_paths"]
    target_path = str(Path(tmp_path).resolve() / "graphify-out" / "graph.json")
    assert target_path in agent["context_paths"]


def test_windsurf_install_existing_corrupted(tmp_path):
    config_dir = tmp_path / ".codeium"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    config_file.write_text("invalid json {", encoding="utf-8")

    integrator = WindsurfIntegrator(project_root=tmp_path)
    assert integrator.install() is True

    backup_file = config_dir / "config.json.bak"
    assert backup_file.exists()
    assert backup_file.read_text(encoding="utf-8") == "invalid json {"

    assert config_file.exists()
    data = json.loads(config_file.read_text(encoding="utf-8"))
    assert data["version"] == "1.0"
    assert "agent" in data


def test_windsurf_uninstall_empty(tmp_path):
    integrator = WindsurfIntegrator(project_root=tmp_path)
    assert integrator.uninstall() is False


def test_windsurf_uninstall_clean(tmp_path):
    integrator = WindsurfIntegrator(project_root=tmp_path)
    assert integrator.install() is True

    config_file = tmp_path / ".codeium" / "config.json"
    assert config_file.exists()

    assert integrator.uninstall() is True
    assert not config_file.exists()
    assert not (tmp_path / ".codeium").exists()


def test_windsurf_uninstall_selective(tmp_path):
    config_dir = tmp_path / ".codeium"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"

    initial_config = {
        "version": "1.0",
        "custom_key": "custom_value",
        "agent": {
            "rules": ["Custom user rule.", _WINDSURF_RULES[0]],
            "context_paths": ["/some/other/path/graph.json"]
        }
    }
    config_file.write_text(json.dumps(initial_config), encoding="utf-8")

    integrator = WindsurfIntegrator(project_root=tmp_path)
    assert integrator.uninstall() is True

    assert config_file.exists()
    data = json.loads(config_file.read_text(encoding="utf-8"))
    assert data["custom_key"] == "custom_value"

    agent = data["agent"]
    assert "Custom user rule." in agent["rules"]
    assert _WINDSURF_RULES[0] not in agent["rules"]
    assert "/some/other/path/graph.json" in agent["context_paths"]

    target_path = str(Path(tmp_path).resolve() / "graphify-out" / "graph.json")
    assert target_path not in agent["context_paths"]


def test_windsurf_cli_project(tmp_path):
    # Test project install/uninstall path
    m._project_install("windsurf", tmp_path)
    config_file = tmp_path / ".codeium" / "config.json"
    assert config_file.exists()

    m._project_uninstall("windsurf", tmp_path)
    assert not config_file.exists()


def test_windsurf_cli_main_subcommand(tmp_path):
    # Test end-to-end CLI integration for install
    test_args_install = ["graphify", "windsurf", "install", "--project"]
    with patch.object(sys, "argv", test_args_install), \
         patch.object(Path, "cwd", return_value=tmp_path):
        m.main()

    config_file = tmp_path / ".codeium" / "config.json"
    assert config_file.exists()

    # Test end-to-end CLI integration for uninstall
    test_args_uninstall = ["graphify", "windsurf", "uninstall", "--project"]
    with patch.object(sys, "argv", test_args_uninstall), \
         patch.object(Path, "cwd", return_value=tmp_path):
        m.main()

    assert not config_file.exists()
