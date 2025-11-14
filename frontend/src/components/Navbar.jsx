import { Link } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const menuItems = [
    { label: "Reportes", link: "/" },
    { label: "Visores", link: "/visors" },
    { label: "Simuladores", link: "/" },
  ];

  return (
    <nav className="w-full bg-[#4B82CF]">
      <div className="max-w-screen-xl mx-auto h-12 flex items-center px-6">
        <div className="flex items-center space-x-8 text-white text-sm font-medium">

          {menuItems.map((item, index) => (
            <Link
              key={index}
              to={item.link}
              className="flex items-center cursor-pointer hover:opacity-90 transition"
            >
              {/* Solo aparece si en el futuro quieres agregar iconos */}
              {item.icon && (
                <span className="text-lg mr-2">☰</span>
              )}

              <span>{item.label}</span>
              <span className="ml-1 text-xs">▼</span>
            </Link>
          ))}

        </div>
      </div>
    </nav>
  );
}