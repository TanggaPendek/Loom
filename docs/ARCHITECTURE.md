# Loom Architecture Documentation

> **Last Updated**: 2026-01-07

## System Overview

Loom is a visual node-based programming system consisting of three main components:

```mermaid
graph LR
    FE[Frontend<br/>React UI] <-->|HTTP/WS| BE[Backend<br/>Project/Node CRUD]
    BE -->|File System| UD[(User Data<br/>Projects)]
    BE -.->|Triggers| EX[Executor Engine<br/>Node Execution]
    EX -->|Reads| NB[(Nodebank<br/>Node Functions)]
    EX -->|Manages| VENV[Virtual Env<br/>Project Dependencies]
```

### Component Responsibilities

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Frontend** | Visual node editor, UI for creating/managing projects | React + Vite |
| **Backend** | CRUD operations for projects and nodes, coordination | Python + SignalHub |
| **Executor** | Node execution engine, dependency resolution, execution | Python + EngineSignalHub |

---

## Backend Architecture

### Module Structure

```
backend/src/
├── main_backend.py          # CLI entry point, command dispatcher
└── modules/
    ├── signal_hub.py         # Backend signal coordination (async)
    ├── execution_manager.py  # Execution coordinator (backend → executor)
    ├── project_manager.py    # Project CRUD operations
    ├── node_manager.py       # Custom node CRUD operations
    └── validator.py          # Payload validation
```

### Backend Signal Flow

```mermaid
sequenceDiagram
    participant CLI as main_backend.py
    participant PM as ProjectManager
    participant NM as NodeManager
    participant EM as ExecutionManager
    participant SH as SignalHub
    participant FS as FileSystem
    
    CLI->>SH: emit("project_init_request", payload)
    SH->>PM: on_project_init_request()
    PM->>FS: Create project folder
    PM->>FS: Save savefile.json
    PM->>SH: emit("file_save", {path})
    PM->>SH: emit("project_init", project_data)
    
    CLI->>SH: emit("engine_run_request", payload)
    SH->>EM: on_run_request()
    EM->>SH: emit("execution_started")
    EM->>SH: emit("initialization_started")
    EM->>SH: emit("engine_run")
    Note over SH: Executor engine listens to engine_run
```

### Key Design Patterns

**Signal-Based Decoupling**
- All modules communicate via `SignalHub`
- No direct function calls between managers
- Easy to add new listeners without modifying existing code

**Request/Response Pattern**
- CLI emits `*_request` signals
- Managers handle requests via `_handle_*` methods
- Managers emit result/status signals

**Validation Layer**
- All inputs validated before processing
- Validation errors emitted as signals
- Prevents invalid data from reaching managers

---

## Executor Architecture

### Module Structure

```
executor/engine/
├── main_engine.py          # Entry point, async orchestration
├── engine_signal.py        # Engine signal hub (async)
├── execution_manager.py    # Sequencer & execution logic
├── node_loader.py          # Dynamic node loading (async)
├── variable_manager.py     # Variable/data flow management (async)
└── venv_manager.py         # Virtual environment management (async)
```

### Async Initialization Flow

One of the key optimizations is concurrent initialization of components:

```mermaid
sequenceDiagram
    participant Main as main_engine.py
    participant EM as ExecutionManager
    participant NL as NodeLoader
    participant VM as VariableManager
    participant VE as VenvManager
    participant SH as EngineSignalHub
    
    Main->>EM: initialize_async(nodes, nodebank_path, project_path)
    
    par Concurrent Initialization
        EM->>NL: preload_nodes_async(nodes)
        NL->>SH: emit("nodeloader_started")
        NL->>NL: Load all nodes concurrently
        NL->>SH: emit("node_loaded") for each
        NL->>SH: emit("nodeloader_completed")
    and
        EM->>VM: init_variables_async(nodes)
        VM->>SH: emit("varmanager_started")
        VM->>VM: Initialize all variables
        VM->>SH: emit("varmanager_initialized")
    and
        EM->>VE: ensure_venv_async()
        VE->>SH: emit("venv_check_started")
        VE->>VE: Create venv if needed
        VE->>VE: Install requirements
        VE->>SH: emit("venv_ready")
    end
    
    Note over EM: All components initialized concurrently!
    EM->>Main: Initialization complete
```

### Execution Pipeline

After initialization, nodes are executed in topological order:

```mermaid
graph TD
    A[Load Graph JSON] --> B[Initialize Components<br/>Concurrent]
    B --> C[Build Dependency Graph]
    C --> D[Topological Sort]
    D --> E[Execute Nodes in Order]
    E --> F{More Nodes?}
    F -->|Yes| E
    F -->|No| G[Emit Final Variables]
    G --> H[Done]
```

### Node Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: Node in graph
    Pending --> Ready: Dependencies completed
    Ready --> Executing: Function called
    Executing --> Success: Output produced
    Executing --> Failed: Exception thrown
    Success --> [*]
    Failed --> [*]
```

---

## Integration Points

### Backend ↔ Executor

**Current Integration**: File-based
- Backend creates/updates `savefile.json`
- Executor reads `savefile.json` for execution
- Communication via signals (if shared SignalHub)

**Future Integration**:  Signal bridge or shared hub could enable real-time communication

### Frontend ↔ Backend

**HTTP REST API** (planned)
- `POST /projects` - Create project
- `GET /projects` - List projects
- `PUT /projects/:id` - Update project
- `DELETE /projects/:id` - Delete project
- `POST /execute` - Trigger execution

**WebSocket** (planned)
- Real-time execution progress updates
- Live variable value updates
- Node execution status

---

## Signal Architecture

Both backend and executor use signal hubs for internal coordination:

| Hub | Location | Purpose |
|-----|----------|---------|
| **SignalHub** | `backend/src/modules/signal_hub.py` | Backend coordination |
| **EngineSignalHub** | `executor/engine/engine_signal.py` | Executor coordination |

### Why Separate Hubs?

- **Separation of Concerns**: Backend and executor have different responsibilities
- **Independent Scalability**: Can run in separate processes/containers
- **Clear Boundaries**: Explicit integration points prevent tight coupling

See [SIGNALS.md](./SIGNALS.md) for complete signal reference.

---

## Data Flow

### Project Creation Flow

```
User Input → Backend CLI → ProjectManager
→ Create folder structure
→ Initialize savefile.json
→ Emit signals
→ Return success
```

### Execution Flow

```
savefile.json → Executor  main_engine.py
→ Initialize (NodeLoader, VenvManager, VariableManager) CONCURRENTLY
→ Build dependency graph
→ Topological sort
→ Execute nodes sequentially
→ Update variables
→ Emit results
```

---

## File System Structure

```
Loom/
├── backend/              # Backend CRUD operations
│   └── src/
│       ├── main_backend.py
│       └── modules/
├── executor/             # Execution engine
│   └── engine/
│       ├── main_engine.py
│       └── *.py
├── nodebank/             # Node function library
│   ├── builtin/          # Built-in nodes
│   └── custom/           # User-defined nodes
├── userdata/             # User projects
│   └── ProjectName/
│       ├── savefile.json # Project graph data
│       ├── venv/         # Project-specific venv
│       └── requirements.txt
└── frontend/             # React UI (separate)
```

---

## Performance Optimizations

### Async Initialization (NEW)

**Before**: Sequential initialization (~3-5 seconds)
```
NodeLoader: 2s → VenvManager: 2s → VariableManager: 0.5s = 4.5s total
```

**After**: Concurrent initialization (~2-3 seconds)
```
NodeLoader ─┐
VenvManager ─┼─→ All run concurrently = ~2s total (limited by slowest)
VarManager ─┘
```

**Speedup**: ~50% reduction in initialization time

### Module Caching

- NodeLoader caches loaded Python modules
- Subsequent executions load faster
- Cache invalidation on node updates

---

## Testing Strategy

See [docs/TESTING.md](./TESTING.md) for complete testing documentation.

**Test Organization**:
- `backend/tests/` - Backend unit tests
- `executor/tests/` - Executor unit tests
- `tests/` - Integration tests

**Test Types**:
- Unit tests for individual modules
- Integration tests for signal flow
- Performance tests for async optimization

---

## Future Enhancements

1. **Parallel Node Execution**: Execute independent nodes concurrently
2. **Distributed Execution**: Run nodes on different machines
3. **Execution Caching**: Cache node outputs for faster re-runs
4. **Live Debugging**: Step through execution, inspect variables
5. **Hot Reload**: Update nodes without restarting execution
