import React, { useState } from 'react';
import { runEngine, stopEngine } from '../api/commands';

const EngineButton = () => {
  // 'idle' = Ready to Run (Green), 'running' = Ready to Stop (Red)
  const [status, setStatus] = useState('idle');
  const [isPending, setIsPending] = useState(false);

  const handleToggle = async () => {
    setIsPending(true); // Disable button while the request is in flight

    try {
      if (status === 'idle') {
        // Send 'run' command to Python
        await runEngine();
        setStatus('running'); // Optimistic change
      } else {
        // Send 'stop' command to Python
        await stopEngine();
        setStatus('idle'); // Forced change back for testing
      }
    } catch (error) {
      console.error("Engine command failed:", error);
    } finally {
      setIsPending(false);
    }
  };

  const isRunning = status === 'running';

  return (
    <button
      onClick={handleToggle}
      disabled={isPending}
      className={`engine-btn ${status}`}
      style={{
        backgroundColor: isRunning ? '#d9534f' : '#5cb85c',
        color: 'white',
        padding: '12px 24px',
        border: 'none',
        borderRadius: '8px',
        cursor: isPending ? 'wait' : 'pointer',
        fontWeight: 'bold',
        transition: 'all 0.2s ease'
      }}
    >
      {isPending ? '...' : isRunning ? '⏹ STOP' : '▶ RUN'}
    </button>
  );
};

export default EngineButton;