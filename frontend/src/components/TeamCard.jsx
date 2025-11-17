import { useState } from "react";
import emailIcon from "../assets/icons/about/email-blue.svg";
import copyIcon from "../assets/icons/about/copy-blue.svg";

export default function TeamCard({
  name,
  lastname,
  position,
  role,
  email,
  picture,
  picture_hover
}) {
  const [hovered, setHovered] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(email);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
    className="group flex flex-col md:flex-row shadow-lg gap-y-2 rounded-2xl
              overflow-hidden transition-all duration-300 w-full max-w-4xl mx-auto h-full"
    onMouseEnter={() => setHovered(true)}
    onMouseLeave={() => setHovered(false)}
  >

    {/* IMAGE SECTION - Always square using aspect-ratio */}
    <div className="flex-shrink-0 p-4 flex items-center justify-center ">
      {/* Mobile */}
      <div
        className="
          md:hidden h-full aspect-square overflow-hidden rounded-2xl
          transition-all duration-300
          group-hover:-translate-y-2 group-hover:-translate-x-2
          group-hover:shadow-[8px_8px_0_0_#4d80c9]
        "
      >
        <img
          src={hovered && picture_hover ? picture_hover : picture}
          alt={`${name} ${lastname}`}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Desktop */}
      <div
        className="
          hidden md:block w-80 aspect-square overflow-hidden rounded-2xl
          transition-all duration-300
          group-hover:-translate-y-2 group-hover:-translate-x-2
          group-hover:shadow-[8px_8px_0_0_#4d80c9]

        "
      >
        <img
          src={hovered && picture_hover ? picture_hover : picture}
          alt={`${name} ${lastname}`}
          className="w-full h-full object-cover"
        />
      </div>
    </div>



      {/* TEXT CONTENT SECTION */}
    <div className=" flex flex-col justify-center flex-grow text-primary-blue space-y-1">

        {/* Name + Position + Role */}
        <div className=" space-y-2 bg-white p-3 mr-12 ml-12">
          <h2 className="text-4xl md:text-4xl font-ancizar font-bold leading-tight ">
            {name} <br/>{lastname}
          </h2>
          
          <div className="space-y-1">
            <p className="text-2xl md:text-2xl font-ancizar">
              {position}
            </p>

            {role && (
              <p className="text-2xl md:text-2xl font-ancizarItalic text-light">
                {role}
              </p>
            )}
          </div>
        </div>

        {/* Email Section */}
        <div className="space-y-1 bg-white mr-12 ml-12">
          <p className="text-m font-semibold bg-white p-1">Correo electrónico</p>

          <div className="flex items-start bg-white">
            {/* Email Icon - Outside the box */}
            <img
              src={emailIcon}
              alt="Email icon"
              className="w-12 h-12 flex-shrink-0 mt-2"
            />

            {/* Email Box */}
            <button
              className="group flex items-center space-x-3 bg-gray-100 p-3 rounded-md
                        hover:bg-gray-200 transition-all duration-200 w-full text-left flex-grow"
              onClick={handleCopyEmail}
            >
              <span className="text-xl text-gray-700 break-all flex-grow">
                {email}
              </span>

              <div className="flex items-center">
                {copied ? (
                  <span className="text-xs text-green-600 font-medium mr-2">
                    ¡Copiado!
                  </span>
                ) : null}
                <img
                  src={copyIcon}
                  alt="Copy icon"
                  className="w-10 h-10 group-hover:opacity-100 flex-shrink-0"
                />
              </div>
            </button>
          </div>
      </div>

    </div>
  </div>
  );
}