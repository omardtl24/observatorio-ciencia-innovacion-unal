import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { getUserInfo, logout, fetchProfileImage } from "../services/authService";

export default function UserProfile() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [imageSrc, setImageSrc] = useState(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const user = getUserInfo();
    setUserInfo(user);
  }, []);

  useEffect(() => {
    let active = true;

    const loadImage = async () => {
      if (!userInfo?.imageId) {
        setImageSrc(null);
        return;
      }

      try {
        const url = await fetchProfileImage(userInfo.imageId);
        if (active) {
          setImageSrc(url);
        }
      } catch (error) {
        if (active) {
          setImageSrc(null);
        }
      }
    };

    loadImage();

    return () => {
      active = false;
    };
  }, [userInfo?.imageId]);

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

  const fullName = `${userInfo.names} ${userInfo.lastNames}`.trim();
  const roleNames = Array.isArray(userInfo.roles) ? userInfo.roles : [];
  const hasAdminRole = roleNames.some((role) => {
    if (typeof role !== "string") {
      return false;
    }

    const normalizedRole = role.trim().toLowerCase();
    return normalizedRole === "administrador" || normalizedRole === "admin" || normalizedRole === "administrator";
  });
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
        className="flex items-center space-x-2 px-3 py-1 rounded-full bg-primary-blue-base border border-white hover:bg-secondary-gray-strong hover:border-primary-blue-strong transition"
        title="User Profile"
      >
        {imageSrc ? (
          <img
            src={imageSrc}
            alt={fullName}
            className="w-8 h-8 rounded-full object-cover border border-gray-300"
          />
        ) : (
          <div className="w-8 h-8 rounded-full bg-primary-blue-strong text-white flex items-center justify-center text-xs font-bold">
            {initials}
          </div>
        )}
        <span className="text-sm font-serif italic text-white hidden sm:inline">
          !Hola {userInfo.names? userInfo.names : "Usuario"}!
        </span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-primary-blue-base rounded-lg shadow-xl z-50 overflow-hidden border border-gray-200">
          {/* User Info Section */}
          <div className="text-white px-3 pt-4 pb-3">
            <div className="flex items-center space-x-3">
              {imageSrc ? (
                <img
                  src={imageSrc}
                  alt={fullName}
                  className="w-12 h-12 rounded-full object-cover border-2 border-white"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-white text-primary-blue flex items-center justify-center text-sm font-bold">
                  {initials}
                </div>
              )}
              <div className="flex-1">
                <p className="font-semibold font-serif italic text-sm">{fullName}</p>
                <p className="text-xs font-serif italic">{userInfo.email}</p>
                <p className="text-xs font-serif italic">Roles: {roleNames.length ? roleNames.join(", ") : "Sin roles asignados"}</p>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="px-3 pb-1">
            <div className="flex items-start gap-3">
              <div className="w-12" aria-hidden="true"></div>
              <div className="flex-1">
                {hasAdminRole && (
                  <button
                    onClick={() => {
                      setIsOpen(false);
                      navigate("/dashboard");
                    }}
                    className="inline-flex mb-2 bg-primary-blue-base hover:bg-white hover:text-primary-blue-strong hover:font-bold border border-primary-blue text-white hover:bg-primary-blue font-sans text-sm px-3 py-0.5 rounded-md transition"
                  >
                    Dashboard
                  </button>
                )}
                <button
                  onClick={() => logout(null, navigate)}
                  className="inline-flex mb-2 bg-secondary-gray-light hover:bg-white  hover:font-bold border border border-primary-blue text-primary-blue-strong hover:bg-primary-blue font-sans text-sm px-3 py-0.5 rounded-md transition"
                >
                  Cerrar sesión
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
