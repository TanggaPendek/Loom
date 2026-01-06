"""Tests for backend SignalHub"""
import pytest
import asyncio


@pytest.mark.unit
def test_signal_hub_basic_emit(signal_hub):
    """Test basic synchronous signal emission."""
    received = []
    
    def handler(payload):
        received.append(payload)
    
    signal_hub.on("test_signal", handler)
    signal_hub.emit("test_signal", {"data": "hello"})
    
    assert len(received) == 1
    assert received[0]["data"] == "hello"


@pytest.mark.unit
def test_signal_hub_multiple_handlers(signal_hub):
    """Test multiple handlers for same signal."""
    call_order = []
    
    signal_hub.on("test", lambda p: call_order.append("first"))
    signal_hub.on("test", lambda p: call_order.append("second"))
    signal_hub.emit("test")
    
    assert len(call_order) == 2
    assert call_order[0] == "first"
    assert call_order[1] == "second"


@pytest.mark.unit
@pytest.mark.async
@pytest.mark.asyncio
async def test_signal_hub_async_handler(signal_hub):
    """Test async handler registration and emission."""
    result = []
    
    async def async_handler(payload):
        await asyncio.sleep(0.01)
        result.append(payload)
    
    signal_hub.on_async("test", async_handler)
    await signal_hub.emit_async("test", {"value": 42})
    
    assert len(result) == 1
    assert result[0]["value"] == 42


@pytest.mark.unit
@pytest.mark.async
@pytest.mark.asyncio
async def test_signal_hub_mixed_handlers(signal_hub):
    """Test mixing sync and async handlers."""
    results = []
    
    def sync_handler(p):
        results.append(("sync", p))
    
    async def async_handler(p):
        await asyncio.sleep(0.01)
        results.append(("async", p))
    
    signal_hub.on("test", sync_handler)
    signal_hub.on_async("test", async_handler)
    
    await signal_hub.emit_async("test", "data")
    
    assert len(results) == 2
    assert results[0][0] == "sync"  # Sync runs first
    assert results[1][0] == "async"


@pytest.mark.unit
def test_signal_hub_handler_removal(signal_hub):
    """Test handler removal with off()."""
    received = []
    
    def handler(p):
        received.append(p)
    
    signal_hub.on("test", handler)
    signal_hub.emit("test", "first")
    assert len(received) == 1
    
    signal_hub.off("test", handler)
    signal_hub.emit("test", "second")
    assert len(received) == 1  # Should still be 1


@pytest.mark.unit
def test_signal_hub_clear(signal_hub):
    """Test clearing all handlers for a signal."""
    received = []
    
    signal_hub.on("test", lambda p: received.append(1))
    signal_hub.on("test", lambda p: received.append(2))
    
    signal_hub.clear("test")
    signal_hub.emit("test")
    
    assert len(received) == 0


@pytest.mark.unit
def test_signal_hub_error_isolation(signal_hub):
    """Test that handler errors don't stop other handlers."""
    results = []
    
    def failing_handler(p):
        raise Exception("Handler failed!")
    
    def working_handler(p):
        results.append("worked")
    
    signal_hub.on("test", failing_handler)
    signal_hub.on("test", working_handler)
    
    signal_hub.emit("test")
    
    # Working handler should still execute  
    assert "worked" in results


@pytest.mark.unit
def test_registered_signals(signal_hub):
    """Test getting list of registered signals."""
    signal_hub.on("sig1", lambda p: None)
    signal_hub.on("sig2", lambda p: None)
    
    signals = signal_hub.registered_signals()
    assert "sig1" in signals
    assert "sig2" in signals
    assert len(signals) == 2
