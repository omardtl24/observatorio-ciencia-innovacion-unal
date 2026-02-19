import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { getUserInfo, getTokenExpiresIn, logout } from "../services/authService";

export default function UserProfile() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const user = getUserInfo();
    setUserInfo(user);

    if (!user) return;

    // Update time remaining immediately and then every second
    const updateTimer = () => {
      const expiresIn = getTokenExpiresIn();
      setTimeRemaining(Math.max(0, expiresIn));
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  if (!userInfo) {
    return null;
  }

  const formatTimeRemaining = (ms) => {
    if (ms <= 0) return "Expired";

    const seconds = Math.floor((ms / 1000) % 60);
    const minutes = Math.floor((ms / 1000 / 60) % 60);
    const hours = Math.floor(ms / 1000 / 60 / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  const fullName = `${userInfo.names} ${userInfo.lastNames}`.trim();
  const initials = fullName
    .split(" ")
    .map((n) => n[0]?.toUpperCase() || "")
    .join("")
    .slice(0, 2);

  return (
    <div ref={dropdownRef} className="relative">
      {/* Profile Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1 rounded-full hover:bg-gray-200 transition"
        title="User Profile"
      >
        {/* User Icon */}
        <svg
          className="w-8 h-8 text-gray-700"
          fill="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
        </svg>
        <span className="text-sm font-medium text-gray-800 hidden sm:inline">
          Perfil
        </span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl z-50 overflow-hidden border border-gray-200">
          {/* User Info Section */}
          <div className="bg-gradient-to-r from-primary-blue-strong to-blue-600 text-white p-4">
            <div className="flex items-center space-x-3">
              {userInfo.picture ? (
                <img
                  src={userInfo.picture}
                  alt={fullName}
                  className="w-12 h-12 rounded-full object-cover border-2 border-white"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-white text-primary-blue flex items-center justify-center text-sm font-bold">
                  {initials}
                </div>
              )}
              <div className="flex-1">
                <p className="font-semibold text-sm">{fullName}</p>
                <p className="text-xs opacity-90">{userInfo.email}</p>
              </div>
            </div>
          </div>

          {/* Session Info */}
          <div className="px-4 py-3 border-b border-gray-200">
            <p className="text-xs text-gray-600 font-semibold">Session expires in:</p>
            <p className="text-lg font-bold text-primary-blue mt-1">
              {formatTimeRemaining(timeRemaining)}
            </p>
          </div>

          {/* Logout Button */}
          <div className="p-3">
            <button
              onClick={() => logout(null, navigate)}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-3 rounded transition flex items-center justify-center space-x-2"
            >
              <span>🚪</span>
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
