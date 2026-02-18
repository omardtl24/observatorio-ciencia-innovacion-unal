import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function ErrorPopup({ error, onClose, redirectTo, autoClose = false, autoCloseDelay = 5000 }) {
  const [isVisible, setIsVisible] = useState(!!error);
  const navigate = useNavigate();

  useEffect(() => {
    if (error) {
      setIsVisible(true);

      let timer;
      if (autoClose) {
        timer = setTimeout(() => {
          handleClose();
        }, autoCloseDelay);
      }

      return () => clearTimeout(timer);
    }
  }, [error, autoClose, autoCloseDelay]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
    
    if (redirectTo) {
      navigate(redirectTo);
    }
  };

  if (!isVisible || !error) return null;

  const errorMessage = typeof error === "string" ? error : error.message || "An unknown error occurred";

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-40 z-40 transition-opacity duration-300"
        onClick={handleClose}
      />

      {/* Error Popup */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-sm px-4">
        <div className="bg-white rounded-lg shadow-2xl overflow-hidden animate-slideIn">
          {/* Header - Red accent for error */}
          <div className="bg-red-500 h-1"></div>

          {/* Content */}
          <div className="p-6 flex gap-4">
            {/* Error Icon */}
            <div className="flex-shrink-0">
              <svg
                className="w-8 h-8 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>

            {/* Message */}
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Error</h3>
              <p className="text-sm text-gray-600 break-words">{errorMessage}</p>
            </div>

            {/* Close Button */}
            <button
              onClick={handleClose}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close error message"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Action Button */}
          <div className="px-6 pb-4">
            <button
              onClick={handleClose}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-md transition-colors duration-200"
            >
              Regresar
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.9);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
          }
        }

        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </>
  );
}
