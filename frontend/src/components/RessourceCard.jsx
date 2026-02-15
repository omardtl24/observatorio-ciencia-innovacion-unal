import reportIcon from "../assets/icons/resources/report-blue.svg";
import simulatorIcon from "../assets/icons/resources/simulator-blue.svg";
import visorIcon from "../assets/icons/resources/visor-blue.svg";
import calendarIcon from "../assets/icons/resources/calendar-blue.svg";
import imageIcon from "../assets/icons/resources/image-blue.svg";

export default function ResourceCard({
  main_title,
  auxiliar_title,
  type,
  updatedAt,
  coverImage,
  resourceType = "report",
}) {
  const symbol =
    {
      report: reportIcon,
      visor: visorIcon,
      simulator: simulatorIcon,
      doc_presentation: reportIcon,
      image: imageIcon,
    }[resourceType] || reportIcon;

  return (
    <div className="flex flex-col md:flex-row w-full max-w-5xl mx-auto rounded-2xl border border-blue-300 bg-primary-cyan-soft overflow-hidden">

      {/* LEFT IMAGE */}
      <div className="md:w-[400px] w-full h-full py-1 px-1 pr-3 pl-3 flex items-center justify-center">
        <div className="w-full aspect-[16/10] rounded-xl border-2 border-blue-400 bg-white flex items-center justify-center">
          <img
            src={coverImage}
            className=" w-full h-full object-cover rounded-xl"
          />
        </div>
      </div>

      {/* RIGHT CONTENT */}
      <div className="flex flex-col justify-center gap-2.5 py-6 pr-5 pl-0 md:ml-0">

        {/* TITLE */}
        <div className="flex items-start gap-1">
          <img src={symbol} alt="" className="w-10 h-10" />
          <div className="flex flex-col">
            <span className="
              text-slg
              text-primary-cyan-strong
              font-medium
            ">
              {main_title}
            </span>
            <span className="
              text-sm
              text-primary-blue-strong
              font-semibold
            ">
              {auxiliar_title}
            </span>
          </div>
        </div>

        {/* TYPE */}
        <div className="flex items-start gap-1">
          <img src={imageIcon} alt="" className="w-10 h-10" />
          <div className="flex flex-col">
            <span className="
              text-sm
              text-primary-cyan-strong
              font-medium
            ">
              Multimedia
            </span>
            <span className="
              text-sm
              text-primary-blue-strong
              font-semibold
            ">
              {type}
            </span>
          </div>
        </div>

        {/* DATE */}
        <div className="flex items-start gap-1">
          <img src={calendarIcon} alt="" className="w-10 h-10" />
          <div className="flex flex-col">
            <span className="
              text-sm
              text-primary-cyan-strong
              font-medium
            ">
              Fecha de actualización
            </span>
            <span className="
              text-sm
              text-primary-blue-strong
              font-semibold
            ">
              {updatedAt}
            </span>
          </div>
        </div>

      </div>
    </div>
  );
}
