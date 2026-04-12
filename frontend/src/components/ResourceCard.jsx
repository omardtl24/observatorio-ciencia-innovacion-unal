import { useState } from "react";
import { useNavigate } from "react-router-dom";
import calendarIcon from "../assets/icons/resources/calendar-blue.svg";
import { stripColorMarkers } from "../services/stringServices.jsx";

export default function ResourceCard({
  id,
  mainTitle,
  updatedAt,
  coverImage,
  hoverCoverImage,
  resourceIcon,
  number,
  spanishResourceType,
  resourceType = "report",
}) {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    navigate(`/resource/${resourceType}/${id}`);
  };

  return (
    <div
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="
        w-full max-w-3xl mx-auto
        border-2 border-primary-blue-strong
        rounded-t-3xl rounded-b-none
        bg-white
        overflow-hidden
        cursor-pointer
        hover:shadow-xl
        transition-all
      "
    >
      {/* TOP COVER (GRAPH STYLE IMAGE) */}
      <div className="w-full overflow-hidden rounded-t-3xl">
        <img
          src={isHovered && hoverCoverImage ? hoverCoverImage : coverImage}
          className="w-full h-full object-cover"
        />
      </div>

      {/* DIVIDER */}
      <div className="border-t border-primary-blue-strong"></div>

      {/* HEADER */}
      
      <div className="text-center py-2">
        <span className="
          text-2xl
          font-serif italic
          font-bold
          text-primary-blue-strong
        ">
          {(spanishResourceType || "recurso").toUpperCase()} {number}
        </span>
      </div>

      {/* DIVIDER */}
      <div className="border-t border-primary-blue-strong"></div>

      {/* DESCRIPTION */}
      <div className="px-2 pb-1 pt-2 flex items-center gap-3">
        <img src={resourceIcon} alt="" className="w-8 h-8" />
        <span className="
          text-primary-blue-strong
          text-m
          font-serif italic
          font-bold
        ">
          {stripColorMarkers(mainTitle)}
        </span>
      </div>

      {/* DATE */}
      <div className="px-2 pb-2 pt-1 flex items-center gap-3">
        <img src={calendarIcon} alt="" className="w-8 h-8" />
        <span className="
          text-primary-blue-strong
          text-m
          font-serif italic
          font-bold
        ">
          Fecha de actualización: {updatedAt}
        </span>
      </div>
    </div>
  );
}