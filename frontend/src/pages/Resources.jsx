import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ResourceCard from "../components/ResourceCard";
import { fetchResources, parseResourcesForCards } from "../services/resourcesServices";
import { datetoString } from "../services/stringServices.jsx";

export default function Resources() {
  const { type } = useParams();
  const navigate = useNavigate();
  const [data_mapper, setDataMapper] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const typeLabels = {
    report: "reportes",
    reports: "reportes",
    simulator: "simuladores",
    simulators: "simuladores",
    visor: "visores",
    visors: "visores",
    document: "documentos",
    documents: "documentos",
  };
  const typeSpanish = typeLabels[type] || "recursos";
  const defaultErrorMessage = `No fue posible consultar los ${typeSpanish}`;

  const images = [
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1491895200222-0fc4a4c35e18?auto=format&fit=crop&w=800&q=80",
  ];

  useEffect(() => {

    if (!type) {
      setError("Resource type not specified");
      setLoading(false);
      return;
    }

    const loadResources = async () => {
      try {
        setLoading(true);
        setError(null);
        const jsonData = await fetchResources(type);
        const parsedData = parseResourcesForCards(type, jsonData);
        setDataMapper(parsedData);
      } catch (err) {
        const message = err?.message ? `${err.message} ${defaultErrorMessage}` : defaultErrorMessage;
        setError(message);
        navigate(`/connection-error?origin=${encodeURIComponent(window.location.pathname)}`);
      } finally {
        setLoading(false);
      }
    };

    loadResources();
  }, [type, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <p className="text-lg text-gray-600">Loading resources...</p>
      </div>
    );
  }

  if (error) {
    return null;
  }

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        {data_mapper.map((item, index) => (
          <ResourceCard
            key={item.id}
            id={item.id}
            title={item.main_title}
            main_title={item.main_title}
            auxiliar_title={item.auxiliar_title}
            type={item.type || 'PDF'}
            updatedAt={datetoString(item.update_at)}
            coverImage={images[index % images.length]}
            resourceType={type}
          />
        ))}
      </div>
    </div>
  );
}