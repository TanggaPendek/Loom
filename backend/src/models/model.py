from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# === Node Object Schema ===
class NodeObject(BaseModel):
    nodeId: str
    positionId: str
    name: str
    position: Dict[str, float]  # e.g. {"x": 120.5, "y": 300.0}
    input: List[str]
    output: List[str]
    ref: str
    metadata: Optional[Dict] = None


# === Project Schema ===
class ProjectMetadata(BaseModel):
    author: str
    description: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastModified: datetime = Field(default_factory=datetime.utcnow)

class Connection(BaseModel):
    connectionId: str
    sourceNodeId: str
    sourceOutput: str
    targetNodeId: str
    targetInput: str
    metadata: Optional[Dict] = None


class ProjectSchema(BaseModel):
    projectId: str
    projectName: str
    projectPath: str
    metadata: ProjectMetadata
    nodes: List[NodeObject]
    connections: List[Connection]


# === Main Payload ===
class ActionRequest(BaseModel):
    action: str          # run, stop, save, load, etc.
    source: str
    target: str
    projectId: str
    payload: Dict        # can contain project or node data depending on action
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponseModel(BaseModel):
    status: str                  # "success" or "error"
    action: str                  # echo back what action was processed
    message: str                 # readable message
    data: Optional[Dict] = None  # optional payload
    timestamp: datetime = Field(default_factory=datetime.utcnow)
