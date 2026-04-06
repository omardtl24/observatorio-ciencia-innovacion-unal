import { useNavigate } from "react-router-dom";
import calendarIcon from "../assets/icons/resources/calendar-blue.svg";
import { stripColorMarkers } from "../services/stringServices.jsx";

export default function ResourceCard({
  id,
  mainTitle,
  updatedAt,
  coverImage,
  number,
  spanishResourceType,
  resourceType = "report",
}) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/resource/${resourceType}/${id}`);
  };

  return (
    <div
      onClick={handleClick}
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
      <div className="w-full aspect-[16/10] overflow-hidden rounded-t-3xl">
        <img
          src={coverImage}
          className="w-full h-full object-cover"
        />
      </div>

      {/* DIVIDER */}
      <div className="border-t border-primary-blue-strong"></div>

      {/* HEADER */}
      
      <div className="text-center py-2">
        <span className="
          text-xl
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
        <img src={calendarIcon} alt="" className="w-6 h-6" />
        <span className="
          text-primary-blue-strong
          text-sm
          font-serif italic
          font-bold
        ">
          {stripColorMarkers(mainTitle)}
        </span>
      </div>

      {/* DATE */}
      <div className="px-2 pb-2 pt-1 flex items-center gap-3">
        <img src={calendarIcon} alt="" className="w-6 h-6" />
        <span className="
          text-primary-blue-strong
          text-sm
          font-serif italic
          font-bold
        ">
          Fecha de actualización: {updatedAt}
        </span>
      </div>
    </div>
  );
}