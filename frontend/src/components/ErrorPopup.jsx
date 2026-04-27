import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function ErrorPopup({ error, onClose, redirectTo, autoClose = false, autoCloseDelay = 5000 }) {
  const [isVisible, setIsVisible] = useState(!!error);
  const navigate = useNavigate();

  const notifyVisibilityChange = (visible) => {
    window.dispatchEvent(
      new CustomEvent("error-popup-visibility", {
        detail: { visible },
      })
    );
  };

  useEffect(() => {
    if (error) {
      setIsVisible(true);
      notifyVisibilityChange(true);

      let timer;
      if (autoClose) {
        timer = setTimeout(() => {
          handleClose();
        }, autoCloseDelay);
      }

      return () => clearTimeout(timer);
    }

    notifyVisibilityChange(false);

    return undefined;
  }, [error, autoClose, autoCloseDelay]);

  const handleClose = () => {
    notifyVisibilityChange(false);
    setIsVisible(false);
    onClose?.();
    
    if (redirectTo) {
      navigate(redirectTo);
    }
  };

  if (!isVisible || !error) return null;

  const errorMessage = typeof error === "string" ? error : error.message || "Ocurrió un error inesperado";

  return (
    <>
      {/* Overlay */}
      <div
        className={`
          fixed inset-0 z-40
          transition-colors duration-300 ease-in-out
          ${isVisible ? "bg-secondary-gray-base" : "bg-white"}
        `}
      />

      {/* Error Popup */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-sm px-4">
        <div className="bg-white rounded-lg border-secondary-gray-strong shadow-2xl overflow-hidden animate-slideIn">

          {/* Content */}
          <div className="p-6 flex gap-4">
            {/* Message */}
            <div className="flex-1">
              <h3 className="text-3xl font-bold text-secondary-gray-strong mb-2 text-center font-serif italic">Error</h3>
              <p className="text-md text-secondary-gray-base text-center break-words px-5">{errorMessage}</p>
            </div>
          </div>

          {/* Action Button */}
          <div className="px-6 pb-4">
            <button
              onClick={handleClose}
              className="mx-auto block w-fit bg-primary-blue-strong hover:bg-secondary-gray-strong text-white px-3 py-2 rounded-md transition-colors"
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
