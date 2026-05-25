import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ResourceCard from "../components/ResourceCard";
import ErrorPopup from "../components/ErrorPopup";
import { fetchResources, parseResourcesForCards } from "../services/resourcesServices";
import { datetoString } from "../services/stringServices.jsx";
import { getPresentationInfo } from "../services/resourceModels";
import { parseRichText, parseColor } from "../services/stringServices.jsx";
import  reportCoverImg  from "../assets/cardImages/reports.png";
import  reportHoveredCoverImg  from "../assets/cardImages/reportsHover.png";
import  visorCoverImg  from "../assets/cardImages/visors.png";
import  visorHoveredCoverImg  from "../assets/cardImages/visorsHover.png";
import  simulatorCoverImg  from "../assets/cardImages/simulators.png";
import  simulatorHoveredCoverImg  from "../assets/cardImages/simulatorsHover.png";
import  documentCoverImg  from "../assets/cardImages/documents.png";
import  documentHoveredCoverImg  from "../assets/cardImages/documentsHover.png";
import reportIcon from "../assets/icons/resources/report-blue.svg";
import visorIcon from "../assets/icons/resources/visor-blue.svg";
import simulatorIcon from "../assets/icons/resources/simulator-blue.svg";
import documentIcon from "../assets/icons/resources/document-blue.svg";

const TYPE_ALIASES = {
  report: "report",
  reports: "report",
  simulator: "simulator",
  simulators: "simulator",
  visor: "visor",
  visors: "visor",
  document: "document",
  documents: "document",
  document_presentation: "document",
  documents_presentation: "document",
  documents_presentations: "document",
};

function normalizeResourceType(resourceType) {
  if (!resourceType) {
    return "report";
  }

  const key = String(resourceType).toLowerCase();
  return TYPE_ALIASES[key] || key;
}

export default function Resources() {
  const { type } = useParams();
  const normalizedType = normalizeResourceType(type);
  const [dataMapper, setDataMapper] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const typeLabels = {
    report: "reporte",
    simulator: "simulador",
    visor: "visor",
    document: "documento",
  };
  const typeSpanish = typeLabels[normalizedType] || "recursos";
  const defaultErrorMessage = `No fue posible consultar los ${typeSpanish}`;
  const presentationInfo = getPresentationInfo(normalizedType);

  const images_icons = {
    report: {
      coverImage: reportCoverImg,
      hoverCoverImage: reportHoveredCoverImg,
      icon: reportIcon
    },
    simulator: {
      coverImage: simulatorCoverImg,
      hoverCoverImage: simulatorHoveredCoverImg,
      icon: simulatorIcon
    },
    visor: {
      coverImage: visorCoverImg,
      hoverCoverImage: visorHoveredCoverImg,
      icon: visorIcon
    },
    document: {
      coverImage: documentCoverImg,
      hoverCoverImage: documentHoveredCoverImg,
      icon: documentIcon
    }
  };

  useEffect(() => {

    if (!type) {
      setError("No se especificó el tipo de recurso");
      setLoading(false);
      return;
    }

    const loadResources = async () => {
      try {
        setLoading(true);
        setError(null);
        const jsonData = await fetchResources(normalizedType);
        const parsedData = parseResourcesForCards(normalizedType, jsonData);
        setDataMapper(parsedData);
      } catch (err) {
        const message = err?.message ? `${err.message} ${defaultErrorMessage}` : defaultErrorMessage;
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    loadResources();
  }, [normalizedType]);

  if (loading) {
    return (
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <p className="text-lg text-gray-600">Cargando recursos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <ErrorPopup
        error={error}
        onClose={() => setError(null)}
        redirectTo="/dashboard"
      />
    );
  }
  
  return (
    <div className="min-h-screen px-6 pt-0 pb-6">
      <div className="mb-10 -mx-6 w-[calc(100%+4rem)] bg-secondary-gray-soft px-12 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-serif italic font-bold text-primary-blue-strong">
            {parseColor(presentationInfo?.title || `Recursos ${typeSpanish}`, "text-secondary-cyan-strong")}
          </h1>
          {presentationInfo?.text ? (
            <div className="mt-4 space-y-4 text-lg leading-7 text-primary-blue-strong whitespace-pre-line">
              {parseRichText(presentationInfo.text, "text-gray-700")}
            </div>
          ) : null}
        </div>
      </div>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        {dataMapper.map((item, index) => {
          const typeImages = images_icons[normalizedType] || images_icons.report;
          return (
            <ResourceCard
              key={item.id}
              id={item.id}
              number={index + 1}
              mainTitle={item.mainTitle}
              spanishResourceType={typeSpanish}
              type={item.type || 'PDF'}
              updatedAt={datetoString(item.updatedAt)}
              resourceIcon={typeImages.icon}
              coverImage={typeImages.coverImage}
              hoverCoverImage={typeImages.hoverCoverImage}
              resourceType={normalizedType}
            />
          );
        })}
      </div>
    </div>
  );
}