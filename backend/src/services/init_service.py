# services/init_service.py
import json
from datetime import datetime
from pathlib import Path
from models.model import ProjectSchema, ProjectMetadata, ResponseModel

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def init_project(projectId: str, projectName: str, projectPath: str, author: str, description: str = ""):
    """
    Initialize a new project with basic metadata and empty node/connection lists.
    """
    try:
        project_file = DATA_DIR / f"{projectId}.json"

        # If already exists
        if project_file.exists():
            return ResponseModel(
                status="error",
                action="init",
                message=f"Project with ID '{projectId}' already exists."
            )

        # Create base schema
        project = ProjectSchema(
            projectId=projectId,
            projectName=projectName,
            projectPath=projectPath,
            metadata=ProjectMetadata(
                author=author,
                description=description
            ),
            nodes=[],
            connections=[]
        )

        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project.model_dump(), f, indent=4, default=str)

        return ResponseModel(
            status="success",
            action="init",
            message=f"Project '{projectName}' initialized successfully.",
            data={"projectId": projectId, "path": str(project_file)}
        )

    except Exception as e:
        return ResponseModel(
            status="error",
            action="init",
            message=str(e)
        )
