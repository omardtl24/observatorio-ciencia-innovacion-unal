import { useState } from "react";
import emailIcon from "../assets/icons/about/email-blue.svg";
import copy_icon from "../assets/icons/about/copy-blue.svg";

export default function TeamCard({ name, lastname, position, role, email, picture, picture_hover }) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className="flex flex-col md:flex-row gap-x-1 shadow-lg overflow-hidden max-w-fit group"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Image */}
      <div className="flex-shrink-0 w-48 lg:w-56 aspect-square md:aspect-auto">
        <img
          src={hovered ? picture_hover : picture}
          alt={`${name} ${lastname}`}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 border-4 border-primary-blue rounded-lg"
        />
      </div>

      {/* Right content area */}
      <div className="flex flex-col flex-1 md:p-3 text-primary-blue">
        {/* Name, Position, Role */}
        <div className="space-y-1 flex-grow bg-white relative p-2 rounded-r-lg">
          <h3 className="font-ancizar font-bold text-3xl leading-tight">
            {name} <br /> {lastname}
          </h3>
          <p className="font-ancizar text-xl">{position}</p>
          <p className="font-ancizarItalic text-lg leading-relaxed">{role}</p>
        </div>

        {/* Email row inside white container */}
        {email && (
          <div className="flex items-center space-x-2 w-full relative mt-2">
            <img src={emailIcon} className="w-9 h-9 flex-shrink-0 bg-white" />
            <div className="flex-1 group flex items-center bg-white rounded-md border border-primary-blue transition-all duration-200 group-hover:bg-secondary-cyan-accent group-hover:text-primary-blue group-hover:border-primary-blue">
              <span className="text-xl font-ancizar flex-1 px-2 truncate">{email}</span>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(email);
                  alert(`Copiado: ${email}`);
                }}
                className="flex-shrink-0 flex items-center"
              >
                <img src={copy_icon} className="w-10 h-10" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
