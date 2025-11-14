import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { isAuthenticated, logout } from "../services/authService";

export default function Dashboard() {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, [navigate]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Retrieve localStorage data
  const name = localStorage.getItem("names") || "Invitado";
  const lastName = localStorage.getItem("last_names") || "";
  const email = localStorage.getItem("email") || "desconocido";
  const image =
    localStorage.getItem("picture") || "https://via.placeholder.com/150";

  return (
    <div className="p-10 flex flex-col items-center">
      {/* USER INFO BLOCK */}
      <div className="flex flex-col md:flex-row items-center justify-center mt-12 gap-10 text-center md:text-left">

        {/* LEFT — IMAGE */}
        <div className="flex flex-col items-center md:items-start">
          <img
            src={image}
            alt="User Avatar"
            className="w-32 h-32 rounded-full mb-4 object-cover"
          />
        </div>

        {/* RIGHT — INFO */}
        <div className="flex flex-col items-center md:items-start text-lg">
          <p>Bienvenido,</p>
          <p className="font-semibold">
            {name} {lastName}!
          </p>
          <p>Email: {email}</p>
        </div>
      </div>

      {/* LOGOUT BUTTON (red, below the info) */}
      <button
        onClick={handleLogout}
        className="mt-10 bg-red-500 text-white px-6 py-3 rounded-xl text-lg shadow-md hover:bg-red-600 transition"
      >
        Logout
      </button>
    </div>
  );
}
