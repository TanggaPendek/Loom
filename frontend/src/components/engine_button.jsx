import React, { useState, useEffect, useRef } from 'react';
import { runEngine, stopEngine, getEngineState } from '../api/commands';
import ErrorModal from './ErrorModal';

const EngineButton = () => {
  // Engine states: 'idle' or 'running'
  const [status, setStatus] = useState('idle');
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState(null);
  const [showErrorModal, setShowErrorModal] = useState(false);

  // Polling reference
  const pollingInterval = useRef(null);

  // Poll engine state from backend
  const pollEngineState = async () => {
    try {
      const response = await getEngineState();

      if (response.status === 'ok') {
        setStatus(response.state); // 'idle' or 'running'

        // Check for errors
        if (response.error) {
          setError(response.error);
          setShowErrorModal(true);
          // Stop polling if error
          stopPolling();
        }
      }
    } catch (err) {
      console.error('Failed to poll engine state:', err);
    }
  };

  // Start polling (every 1 second)
  const startPolling = () => {
    if (!pollingInterval.current) {
      pollingInterval.current = setInterval(pollEngineState, 1000);
    }
  };

  // Stop polling
  const stopPolling = () => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
  };

  // Effect: Poll when running, stop when idle
  useEffect(() => {
    if (status === 'running') {
      startPolling();
    } else {
      stopPolling();
    }

    // Cleanup on unmount
    return () => stopPolling();
  }, [status]);

  // Initial state check on mount
  useEffect(() => {
    pollEngineState();
  }, []);

  const handleToggle = async () => {
    setIsPending(true);

    try {
      if (status === 'idle') {
        // Send 'run' command
        const result = await runEngine();

        if (result.status === 'ok') {
          setStatus('running'); // Optimistic update
          startPolling(); // Start polling immediately
        } else if (result.status === 'error') {
          setError({ message: result.message });
          setShowErrorModal(true);
        }
      } else {
        // Send 'stop' command
        await stopEngine();
        // Don't optimistically set to idle - let polling handle it
      }
    } catch (err) {
      console.error('Engine command failed:', err);
      setError({ message: err.message || 'Unknown error occurred' });
      setShowErrorModal(true);
    } finally {
      setIsPending(false);
    }
  };

  const closeErrorModal = () => {
    setShowErrorModal(false);
    setError(null);
  };

  const isRunning = status === 'running';

  return (
    <>
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

      <ErrorModal
        isOpen={showErrorModal}
        error={error}
        onClose={closeErrorModal}
      />
    </>
  );
};

export default EngineButton;