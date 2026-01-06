import pytest
from backend.src.modules.signal_hub import SignalHub

def test_signal_hub_emit():
    hub = SignalHub()
    received = []
    
    def handler(payload):
        received.append(payload)
        
    hub.on("test_signal", handler)
    hub.emit("test_signal", {"data": "hello"})
    
    assert len(received) == 1
    assert received[0] == {"data": "hello"}

def test_signal_hub_multiple_handlers():
    hub = SignalHub()
    received = []
    
    hub.on("test_signal", lambda p: received.append(1))
    hub.on("test_signal", lambda p: received.append(2))
    hub.emit("test_signal")
    
    assert len(received) == 2
    assert 1 in received
    assert 2 in received

def test_signal_hub_registered_signals():
    hub = SignalHub()
    hub.on("sig1", lambda p: None)
    hub.on("sig2", lambda p: None)
    
    signals = hub.registered_signals()
    assert "sig1" in signals
    assert "sig2" in signals
    assert len(signals) == 2
