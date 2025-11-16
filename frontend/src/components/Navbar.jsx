import { Link } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const [openIndex, setOpenIndex] = useState(null);

  const menuItems = [
    { 
      label: "Observatorio",
      children: [
        { label: "Conócenos", link: "/conocenos" },
      ]
    },
    { 
      label: "Reportes",
      children: [
        { label: "Mensuales", link: "/" },
        { label: "Anuales", link: "/" },
      ]
    },
    { 
      label: "Visores",
      children: [
        { label: "Dashboard 1", link: "/visors/1" },
        { label: "Dashboard 2", link: "/" },
      ]
    },
    { 
      label: "Simuladores",
      children: [
        { label: "Modelo A", link: "/" },
        { label: "Modelo B", link: "/" },
      ]
    },
  ];

  return (
    <nav className="w-full bg-primary-blue font-ancizar">
      <div className="max-w-screen-xl mx-auto h-12 flex items-center px-6 justify-center">
        <div className="flex items-center space-x-10 text-white text-sm md:text-lg">

          {menuItems.map((item, index) => (
            <div key={index} className="relative">

              {/* Top-level button */}
              <button
                className="flex items-center cursor-pointer hover:opacity-90 transition"
                onClick={() =>
                  setOpenIndex(openIndex === index ? null : index)
                }
              >
                <span>{item.label}</span>
                <span className="ml-1 text-xs">▼</span>
              </button>

              {/* Dropdown */}
              {item.children && (
                <div
                  className={`
                    absolute left-0 mt-2 bg-white text-black rounded shadow-lg
                    py-2 w-48 z-50 transition-all duration-150
                    ${openIndex === index ? "opacity-100 visible" : "opacity-0 invisible"}
                  `}
                >
                  {item.children.map((child, childIndex) => (
                    <Link
                      key={childIndex}
                      to={child.link}
                      className="block px-4 py-2 hover:bg-gray-100"
                      onClick={() => setOpenIndex(null)} // Close after selection
                    >
                      {child.label}
                    </Link>
                  ))}
                </div>
              )}

            </div>
          ))}

        </div>
      </div>
    </nav>
  );
}
