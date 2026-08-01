import json
from pathlib import Path

class WindsurfIntegrator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config_dir = self.project_root / ".codeium"
        self.config_file = self.config_dir / "config.json"

    def install(self) -> bool:
        """Configures Windsurf's Flow state to actively track Graphify indices."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            
            windsurf_config = {
                "version": "1.0",
                "agent": {
                    "rules": [
                        "Prioritize semantic knowledge graphs located in graphify-out/graph.json for codebase context.",
                        "Use graphify-out/graph_report.md to understand overarching module dependencies before refactoring."
                    ],
                    "context_paths": [
                        str(self.project_root / "graphify-out" / "graph.json")
                    ]
                }
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(windsurf_config, f, indent=4)

            print(f"Successfully configured Windsurf integration at: {self.config_file}")
            return True

        except Exception as e:
            print(f"Failed to install Windsurf configuration: {e}")
            return False

    def uninstall(self) -> bool:
        """Removes Windsurf configuration files to clean up the workspace."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
                
                if not any(self.config_dir.iterdir()):
                    self.config_dir.rmdir()
                print("Successfully removed Windsurf configurations.")
                return True
            print("No Windsurf configuration found to remove.")
            return False
        except Exception as e:
            print(f"Failed to uninstall Windsurf configuration: {e}")
            return False
