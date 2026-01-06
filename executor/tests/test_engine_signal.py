"""Tests for executor EngineSignalHub"""
import pytest
import asyncio


@pytest.mark.unit
def test_engine_signal_hub_basic_emit(engine_signal_hub):
    """Test basic synchronous signal emission."""
    received = []
    
    def handler(payload):
        received.append(payload)
    
    engine_signal_hub.on("test_signal", handler)
    engine_signal_hub.emit("test_signal", {"data": "hello"})
    
    assert len(received) == 1
    assert received[0]["data"] == "hello"


@pytest.mark.unit
@pytest.mark.async
@pytest.mark.asyncio
async def test_engine_signal_hub_async(engine_signal_hub):
    """Test async handler registration and emission."""
    result = []
    
    async def async_handler(payload):
        await asyncio.sleep(0.01)
        result.append(payload)
    
    engine_signal_hub.on_async("test", async_handler)
    await engine_signal_hub.emit_async("test", {"value": 123})
    
    assert len(result) == 1
    assert result[0]["value"] == 123


@pytest.mark.unit
def test_engine_signal_hub_error_isolation(engine_signal_hub):
    """Test that handler errors don't stop other handlers."""
    results = []
    
    def failing_handler(p):
        raise Exception("Handler failed!")
    
    def working_handler(p):
        results.append("worked")
    
    engine_signal_hub.on("test", failing_handler)
    engine_signal_hub.on("test", working_handler)
    
    engine_signal_hub.emit("test")
    
    # Working handler should still execute
    assert "worked" in results
