import json
from pathlib import Path

_WINDSURF_RULES = [
    "Prioritize semantic knowledge graphs located in graphify-out/graph.json for codebase context.",
    "Use graphify-out/graph_report.md to understand overarching module dependencies before refactoring."
]

class WindsurfIntegrator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config_dir = self.project_root / ".codeium"
        self.config_file = self.config_dir / "config.json"

    def install(self) -> bool:
        """Configures Windsurf's Flow state to actively track Graphify indices without clobbering existing configuration."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            config = None
            if self.config_file.exists():
                try:
                    config = json.loads(self.config_file.read_text(encoding="utf-8"))
                except Exception as e:
                    print(f"Existing Windsurf config.json was corrupted. Backing up and recreating: {e}")
                    backup_path = self.config_file.with_suffix(".json.bak")
                    try:
                        self.config_file.rename(backup_path)
                        print(f"Backed up corrupted config to: {backup_path}")
                    except Exception:
                        pass
                    config = None

            if not isinstance(config, dict):
                config = {
                    "version": "1.0",
                    "agent": {
                        "rules": [],
                        "context_paths": []
                    }
                }

            if "version" not in config:
                config["version"] = "1.0"

            if "agent" not in config or not isinstance(config["agent"], dict):
                config["agent"] = {}

            agent = config["agent"]
            if "rules" not in agent or not isinstance(agent["rules"], list):
                agent["rules"] = []
            if "context_paths" not in agent or not isinstance(agent["context_paths"], list):
                agent["context_paths"] = []

            # Add rules if not present
            for rule in _WINDSURF_RULES:
                if rule not in agent["rules"]:
                    agent["rules"].append(rule)

            # Add context path if not present
            target_path = str(self.project_root / "graphify-out" / "graph.json")
            if target_path not in agent["context_paths"]:
                agent["context_paths"].append(target_path)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            print(f"Successfully configured Windsurf integration at: {self.config_file}")
            return True

        except Exception as e:
            print(f"Failed to install Windsurf configuration: {e}")
            return False

    def uninstall(self) -> bool:
        """Selectively removes Graphify configuration from Windsurf, keeping other settings intact."""
        try:
            if not self.config_file.exists():
                print("No Windsurf configuration found to remove.")
                return False

            try:
                config = json.loads(self.config_file.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"Failed to parse Windsurf config.json during uninstall: {e}")
                return False

            if not isinstance(config, dict):
                print("Windsurf config.json format is invalid, skipping uninstallation.")
                return False

            if "agent" in config and isinstance(config["agent"], dict):
                agent = config["agent"]
                if "rules" in agent and isinstance(agent["rules"], list):
                    agent["rules"] = [r for r in agent["rules"] if r not in _WINDSURF_RULES]

                target_path = str(self.project_root / "graphify-out" / "graph.json")
                if "context_paths" in agent and isinstance(agent["context_paths"], list):
                    agent["context_paths"] = [p for p in agent["context_paths"] if p != target_path]

                # Clean up empty agent section if possible
                if "rules" in agent and not agent["rules"]:
                    del agent["rules"]
                if "context_paths" in agent and not agent["context_paths"]:
                    del agent["context_paths"]

                if not agent:
                    del config["agent"]

            # Check if there is anything left besides version
            has_other_keys = any(k != "version" for k in config.keys())

            if not has_other_keys:
                # If nothing besides version remains, we can safely delete the file
                self.config_file.unlink()
                print("Successfully removed Windsurf configurations.")

                # Try to clean up .codeium directory if empty
                try:
                    if not any(self.config_dir.iterdir()):
                        self.config_dir.rmdir()
                        print("Removed empty .codeium directory.")
                except Exception:
                    pass
            else:
                # Otherwise, write the cleaned configuration back
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4)
                print("Successfully removed Graphify rules and paths from Windsurf configurations.")

            return True

        except Exception as e:
            print(f"Failed to uninstall Windsurf configuration: {e}")
            return False
