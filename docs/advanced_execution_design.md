# Advanced Execution Design

This document outlines the vision and implementation strategy for advanced node execution patterns in Loom, including conditional branching, loops, parallel execution, and event-driven nodes.

> [!IMPORTANT]
> This is a **design document only**. No implementation changes will be made to the current execution manager to maintain stability. This serves as a blueprint for future development.

## Table of Contents

1. [Overview](#overview)
2. [Current Architecture](#current-architecture)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Details](#implementation-details)
5. [Migration Strategy](#migration-strategy)
6. [Testing Strategy](#testing-strategy)
7. [Example Use Cases](#example-use-cases)

---

## Overview

### Vision

Enable Loom to support complex execution patterns:
- **Conditional Execution**: Nodes that branch based on boolean conditions
- **Loops**: For/while loops with iteration state management
- **Parallel Execution**: Independent branches running concurrently
- **Infinite Loops**: Long-running nodes for servers/UI applications
- **Event-Driven Nodes**: Respond to external triggers (file changes, HTTP requests, timers)

### Goals

1. Maintain backward compatibility with existing sequential execution
2. Support dynamic Python function loading
3. Prevent infinite loops with configurable iteration limits
4. Enable graceful shutdown of long-running processes
5. Provide clear error messages for graph validation

---

## Current Architecture

### Execution Flow

```python
# Current execution_manager.py (simplified)
async def run_async(self):
    remaining_inbound = self.incoming_count.copy()
    
    while self.ready_queue:
        node_id = self.ready_queue.popleft()
        func = self.functions.get(node_id)
        
        # Gather inputs
        inputs = []
        i = 0
        while (node_id, i) in self.input_buckets:
            inputs.append(self.input_buckets[(node_id, i)])
            i += 1
        
        # Execute
        result = func(*inputs)
        if asyncio.iscoroutine(result):
            result = await result
        
        # Route outputs
        for src_port, tgt_id, tgt_port in self.outgoing.get(node_id, []):
            value = result[src_port]
            self.input_buckets[(tgt_id, tgt_port)] = value
            
            remaining_inbound[tgt_id] -= 1
            if remaining_inbound[tgt_id] <= 0:
                self.ready_queue.append(tgt_id)
```

### Key Characteristics

- **Topological Sort**: Nodes execute in dependency order
- **Queue-Based**: Ready queue manages execution flow
- **Synchronous Flow**: One node completes before next starts
- **No Branching**: Single linear execution path

---

## Proposed Architecture

### Core Components

#### 1. Execution Strategy Pattern

```python
from abc import ABC, abstractmethod

class ExecutionStrategy(ABC):
    """Base class for execution strategies."""
    
    @abstractmethod
    async def execute(self, node: dict, inputs: list, context: dict) -> any:
        """Execute node with given strategy."""
        pass

class SequentialStrategy(ExecutionStrategy):
    """Standard sequential execution (current behavior)."""
    async def execute(self, node: dict, inputs: list, context: dict):
        func = context['functions'][node['nodeId']]
        result = func(*inputs)
        if asyncio.iscoroutine(result):
            result = await result
        return result

class ConditionalStrategy(ExecutionStrategy):
    """Conditional branching execution."""
    async def execute(self, node: dict, inputs: list, context: dict):
        # Execute condition function
        condition_func = context['functions'][node['nodeId']]
        condition_result = condition_func(*inputs)
        
        # Determine branch
        metadata = node.get('metadata', {})
        if condition_result:
            next_nodes = metadata.get('true_path', [])
        else:
            next_nodes = metadata.get('false_path', [])
        
        # Add next nodes to execution queue
        for next_node_id in next_nodes:
            context['ready_queue'].append(next_node_id)
        
        return condition_result

class LoopStrategy(ExecutionStrategy):
    """Loop execution with iteration tracking."""
    async def execute(self, node: dict, inputs: list, context: dict):
        metadata = node.get('metadata', {})
        loop_type = metadata.get('loop_type', 'while')
        max_iterations = metadata.get('max_iterations', 1000)
        loop_back_to = metadata.get('loop_back_to')
        
        # Initialize loop state if not exists
        node_id = node['nodeId']
        if node_id not in context['loop_state']:
            context['loop_state'][node_id] = {'iteration': 0}
        
        loop_state = context['loop_state'][node_id]
        
        # Check iteration limit
        if loop_state['iteration'] >= max_iterations:
            raise RuntimeError(f"Loop {node_id} exceeded max iterations ({max_iterations})")
        
        # Execute loop body
        func = context['functions'][node_id]
        result = func(*inputs)
        if asyncio.iscoroutine(result):
            result = await result
        
        # Check loop condition
        should_continue = result  # Assuming result is boolean
        
        if should_continue and loop_back_to:
            # Add loop target back to queue
            context['ready_queue'].append(loop_back_to)
            loop_state['iteration'] += 1
        else:
            # Loop complete
            loop_state['iteration'] = 0
        
        return result
```

#### 2. Execution Context

```python
class ExecutionContext:
    """Manages runtime state for complex execution patterns."""
    
    def __init__(self):
        self.functions: Dict[str, callable] = {}
        self.input_buckets: Dict[Tuple[str, int], Any] = {}
        self.ready_queue = deque()
        
        # Advanced execution state
        self.loop_state: Dict[str, dict] = {}  # {node_id: {iteration: N, ...}}
        self.branch_state: Dict[str, dict] = {}  # {node_id: {path_taken: 'true'|'false'}}
        self.event_queue: List[dict] = []  # [{event_type, data, target_node}]
        self.parallel_tasks: Dict[str, asyncio.Task] = {}  # {node_id: task}
        
        # Control flags
        self.stop_requested = False
        self.max_iterations = 1000
```

#### 3. Enhanced Execution Manager

```python
class ExecutionManager:
    def __init__(self, nodes, connections, signal_hub=None):
        self.nodes: Dict[str, dict] = {}
        self.connections = connections
        self.signal_hub = signal_hub
        
        # Execution context
        self.context = ExecutionContext()
        
        # Strategy mapping
        self.strategies = {
            'sequential': SequentialStrategy(),
            'conditional': ConditionalStrategy(),
            'loop': LoopStrategy(),
            'parallel': ParallelStrategy(),
            'event': EventStrategy(),
        }
    
    def get_execution_mode(self, node: dict) -> str:
        """Determine execution mode for node."""
        metadata = node.get('metadata', {})
        return metadata.get('execution_mode', 'sequential')
    
    async def execute_node(self, node_id: str):
        """Execute a single node with appropriate strategy."""
        node = self.nodes[node_id]
        
        # Gather inputs
        inputs = []
        i = 0
        while (node_id, i) in self.context.input_buckets:
            inputs.append(self.context.input_buckets[(node_id, i)])
            i += 1
        
        # Get execution strategy
        execution_mode = self.get_execution_mode(node)
        strategy = self.strategies.get(execution_mode, self.strategies['sequential'])
        
        # Execute with strategy
        result = await strategy.execute(node, inputs, vars(self.context))
        
        # Normalize outputs
        if not isinstance(result, (list, tuple)):
            result = [result]
        
        return result
    
    async def run_async(self):
        """Enhanced run loop supporting multiple execution patterns."""
        remaining_inbound = self.incoming_count.copy()
        
        while self.context.ready_queue and not self.context.stop_requested:
            node_id = self.context.ready_queue.popleft()
            
            # Skip if function not loaded
            if node_id not in self.context.functions:
                continue
            
            # Execute node
            try:
                result = await self.execute_node(node_id)
            except Exception as e:
                print(f"[ExecutionManager] Node {node_id} failed: {e}")
                if self.signal_hub:
                    self.signal_hub.emit("execution_error", {
                        "nodeId": node_id,
                        "error": str(e)
                    })
                continue
            
            # Route outputs (same as before)
            for src_port, tgt_id, tgt_port in self.outgoing.get(node_id, []):
                if src_port >= len(result):
                    continue
                
                value = result[src_port]
                self.context.input_buckets[(tgt_id, tgt_port)] = value
                
                remaining_inbound[tgt_id] -= 1
                if remaining_inbound[tgt_id] <= 0:
                    self.context.ready_queue.append(tgt_id)
            
            # Signal completion
            if self.signal_hub:
                self.signal_hub.emit("node_executed", {
                    "nodeId": node_id,
                    "output": result
                })
    
    def request_stop(self):
        """Request graceful shutdown."""
        self.context.stop_requested = True
```

---

## Implementation Details

### Parallel Execution Strategy

```python
class ParallelStrategy(ExecutionStrategy):
    """Execute multiple independent branches concurrently."""
    
    async def execute(self, node: dict, inputs: list, context: dict):
        metadata = node.get('metadata', {})
        parallel_branches = metadata.get('parallel_branches', [])
        
        # Create tasks for each branch
        tasks = []
        for branch_nodes in parallel_branches:
            task = asyncio.create_task(
                self._execute_branch(branch_nodes, context)
            )
            tasks.append(task)
        
        # Wait for all branches to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for errors
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            raise RuntimeError(f"Parallel execution errors: {errors}")
        
        return results
    
    async def _execute_branch(self, branch_nodes: List[str], context: dict):
        """Execute a single branch of parallel execution."""
        for node_id in branch_nodes:
            # Execute each node in sequence within this branch
            node = context['nodes'][node_id]
            func = context['functions'][node_id]
            
            # Get inputs for this node
            inputs = []
            i = 0
            while (node_id, i) in context['input_buckets']:
                inputs.append(context['input_buckets'][(node_id, i)])
                i += 1
            
            # Execute
            result = func(*inputs)
            if asyncio.iscoroutine(result):
                result = await result
            
            # Store result for downstream nodes
            # (implementation details omitted for brevity)
        
        return "Branch complete"
```

### Event-Driven Strategy

```python
class EventStrategy(ExecutionStrategy):
    """Execute nodes in response to external events."""
    
    async def execute(self, node: dict, inputs: list, context: dict):
        metadata = node.get('metadata', {})
        event_type = metadata.get('event_type')  # 'file_change', 'http_request', 'timer'
        
        if event_type == 'timer':
            interval = metadata.get('interval', 1.0)
            while not context.get('stop_requested', False):
                await asyncio.sleep(interval)
                # Trigger downstream nodes
                self._trigger_outputs(node, context)
        
        elif event_type == 'file_change':
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class NodeEventHandler(FileSystemEventHandler):
                def __init__(self, callback):
                    self.callback = callback
                
                def on_modified(self, event):
                    self.callback(event)
            
            watch_path = metadata.get('watch_path', '.')
            observer = Observer()
            handler = NodeEventHandler(lambda e: self._trigger_outputs(node, context))
            observer.schedule(handler, watch_path, recursive=False)
            observer.start()
            
            # Wait until stop requested
            while not context.get('stop_requested', False):
                await asyncio.sleep(0.1)
            
            observer.stop()
            observer.join()
        
        return "Event listener active"
    
    def _trigger_outputs(self, node, context):
        """Trigger execution of downstream nodes."""
        node_id = node['nodeId']
        for src_port, tgt_id, tgt_port in context['outgoing'].get(node_id, []):
            context['ready_queue'].append(tgt_id)
```

---

## Migration Strategy

### Phase 1: Infrastructure (Week 1-2)

1. **Create execution strategy classes** without replacing current logic
2. **Add execution_mode field** to node metadata schema
3. **Create ExecutionContext class** to manage advanced state
4. **Add unit tests** for each strategy in isolation

### Phase 2: Integration (Week 3-4)

1. **Refactor execute_node method** to use strategies
2. **Maintain backward compatibility** by defaulting to sequential
3. **Add integration tests** for strategy switching
4. **Update documentation** with new node metadata fields

### Phase 3: Rollout (Week 5-6)

1. **Create example nodes** for each execution pattern
2. **Add UI controls** for setting execution_mode
3. **Implement validation** for graph structures
4. **Beta test** with power users
5. **Full release** with tutorials and examples

---

## Testing Strategy

### Unit Tests

```python
# test_execution_strategies.py
import pytest
from executor.engine.execution_strategies import ConditionStrategy, LoopStrategy

@pytest.mark.asyncio
async def test_conditional_strategy_true_path():
    strategy = ConditionalStrategy()
    
    node = {
        'nodeId': 'cond_1',
        'metadata': {
            'execution_mode': 'conditional',
            'true_path': ['node_2'],
            'false_path': ['node_3']
        }
    }
    
    context = {
        'functions': {'cond_1': lambda x: x > 10},
        'ready_queue': deque(),
        'nodes': {}
    }
    
    result = await strategy.execute(node, [15], context)
    
    assert result == True
    assert 'node_2' in context['ready_queue']
    assert 'node_3' not in context['ready_queue']

@pytest.mark.asyncio
async def test_loop_strategy_max_iterations():
    strategy = LoopStrategy()
    
    node = {
        'nodeId': 'loop_1',
        'metadata': {
            'execution_mode': 'loop',
            'loop_type': 'while',
            'max_iterations': 10,
            'loop_back_to': 'node_2'
        }
    }
    
    context = {
        'functions': {'loop_1': lambda: True},  # Always continue
        'ready_queue': deque(),
        'loop_state': {},
        'nodes': {}
    }
    
    # Execute 10 times should work
    for _ in range(10):
        await strategy.execute(node, [], context)
    
    # 11th time should raise
    with pytest.raises(RuntimeError, match="exceeded max iterations"):
        await strategy.execute(node, [], context)
```

### Integration Tests

```python
# test_execution_manager_advanced.py
@pytest.mark.asyncio
async def test_conditional_branching_integration():
    """Test full graph with conditional branching."""
    nodes = [
        {'nodeId': 'input_1', ...},
        {'nodeId': 'condition_1', 'metadata': {'execution_mode': 'conditional', ...}},
        {'nodeId': 'true_branch', ...},
        {'nodeId': 'false_branch', ...}
    ]
    
    connections = [
        {'sourceNodeId': 'input_1', 'targetNodeId': 'condition_1', ...},
        # Conditional outputs handled by strategy
    ]
    
    manager = ExecutionManager(nodes, connections)
    await manager.initialize_async(nodes)
    await manager.run_async()
    
    # Assert correct branch was taken
    assert manager.context.branch_state['condition_1']['path_taken'] == 'true'
```

---

## Example Use Cases

### Use Case 1: Web Server Loop

```python
# Graph structure
nodes = [
    {
        'nodeId': 'server_loop',
        'metadata': {
            'execution_mode': 'loop',
            'loop_type': 'infinite',
            'max_iterations': -1  # Infinite
        }
    },
    {'nodeId': 'handle_request', ...},
    {'nodeId': 'send_response', ...}
]
```

### Use Case 2: Conditional Data Processing

```python
nodes = [
    {'nodeId': 'load_data', ...},
    {
        'nodeId': 'check_size',
        'metadata': {
            'execution_mode': 'conditional',
            'condition_func': 'is_large_dataset',
            'true_path': ['parallel_process'],
            'false_path': ['sequential_process']
        }
    },
    {'nodeId': 'parallel_process', 'metadata': {'execution_mode': 'parallel', ...}},
    {'nodeId': 'sequential_process', ...}
]
```

### Use Case 3: Parallel API Calls

```python
nodes = [
    {'nodeId': 'prepare_requests', ...},
    {
        'nodeId': 'parallel_api',
        'metadata': {
            'execution_mode': 'parallel',
            'parallel_branches': [
                ['call_api_1'],
                ['call_api_2'],
                ['call_api_3']
            ]
        }
    },
    {'nodeId': 'merge_results', ...}
]
```

---

## Conclusion

This design provides a flexible, extensible architecture for advanced execution patterns while maintaining backward compatibility. The strategy pattern allows easy addition of new execution modes without modifying core logic.

### Next Steps

1. Review and approve this design document
2. Create detailed implementation tickets for each phase
3. Set up benchmark tests for performance comparison
4. Begin Phase 1 infrastructure development

### Open Questions

1. Should we support nested loops?
2. How to handle event cleanup on graph stop?
3. Should parallel branches share state or be isolated?
4. What debugging tools are needed for complex graphs?
