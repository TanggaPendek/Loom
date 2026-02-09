import React from 'react';
import './ErrorModal.css';

const ErrorModal = ({ isOpen, error, onClose }) => {
    if (!isOpen || !error) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>⚠ Engine Error</h2>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>

                <div className="modal-body">
                    <p className="error-message">{error.message}</p>
                    {error.timestamp && (
                        <p className="error-timestamp">
                            <small>Time: {new Date(error.timestamp).toLocaleString()}</small>
                        </p>
                    )}
                </div>

                <div className="modal-footer">
                    <button className="btn-primary" onClick={onClose}>
                        Dismiss
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ErrorModal;
