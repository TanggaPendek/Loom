import json
from pathlib import Path
from .node_parser import NodeParser  # FIXED IMPORT

class IndexService:
    def __init__(self, project_base: Path, node_bank_path: Path, signal_hub):
        self.project_base = Path(project_base)
        self.node_bank_path = Path(node_bank_path)

        self.project_index_path = self.project_base / "projectindex.json"
        self.node_index_path = self.node_bank_path / "nodeindex.json"

        # 🔥 register listeners ONCE at startup
        signal_hub.on_async("hot_reload_all", self.hot_reload_all)
        signal_hub.on_async("project_hot_reload", self.refresh_projects)
        signal_hub.on_async("node_hot_reload", self.refresh_nodes)

    # -------------------------
    # HOT RELOAD
    # -------------------------
    async def hot_reload_all(self, _payload=None):
        print("[INDEX] 🔥 Hot reload ALL")
        await self.refresh_projects()
        await self.refresh_nodes()

    # -------------------------
    # PROJECT INDEX
    # -------------------------
    async def refresh_projects(self, _payload=None):
        print("[INDEX] Reloading projects...")
        index = []

        if not self.project_base.exists():
            return

        for folder in self.project_base.iterdir():
            if not folder.is_dir():
                continue

            savefile = folder / "savefile.json"
            if not savefile.exists():
                continue

            try:
                with open(savefile, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    index.append({
                        "projectId": data.get("projectId"),
                        "projectName": data.get("projectName"),
                        "lastModified": data.get("metadata", {}).get("lastModified", ""),
                        "projectPath": str(savefile)
                    })
            except Exception as e:
                print(f"[INDEX ERROR] {folder.name}: {e}")

        with open(self.project_index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=4)

        print(f"[INDEX] Projects indexed")

        #print(f"[INDEX] Projects indexed: {len(index)}")

    # -------------------------
    # NODE INDEX
    # -------------------------
    async def refresh_nodes(self, _payload=None):
        print("[INDEX] Reloading nodes...")
        all_nodes = []

        for folder_name in ("builtin", "custom"):
            folder_path = self.node_bank_path / folder_name
            if not folder_path.exists():
                continue

            for py_file in folder_path.glob("*.py"):
                try:
                    all_nodes.extend(NodeParser.parse_python_file(py_file))
                except Exception as e:
                    print(f"[NODE ERROR] {py_file.name}: {e}")

        with open(self.node_index_path, "w", encoding="utf-8") as f:
            json.dump(all_nodes, f, indent=4)
        print(f"[INDEX] Projects indexed")
        #print(f"[INDEX] Nodes indexed: {len(all_nodes)}")
