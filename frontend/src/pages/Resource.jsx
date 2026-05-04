import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ResourceDisplay from "../components/ResourceDisplay";
import ResourceDataSourcesList from "../components/ResourceDataSourcesList";
import ErrorPopup from "../components/ErrorPopup";
import { fetchResource, parseResourcesText } from "../services/resourcesServices";
import { parseRichText, parseColor } from "../services/stringServices.jsx";
import { isAuthenticated, redirectToLogin } from "../services/authService";

export default function Resource() {
  const { type, id } = useParams();
  const navigate = useNavigate();
  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is authenticated, if not redirect to login
    if (!isAuthenticated()) {
      redirectToLogin(navigate, `/resource/${type || ""}/${id || ""}`, type || null);
      return;
    }

    if (!type || !id) {
      setError("Debes indicar el tipo de recurso y su identificador");
      setLoading(false);
      return;
    }

    const loadResource = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchResource(type, id);
        const parsedData = parseResourcesText(type, data);
        setResource(parsedData);
      } catch (err) {
        // Check if it's an authentication error
        if (err.message && err.message.includes("401")) {
          redirectToLogin(navigate, `/resource/${type || ""}/${id || ""}`, type || null);
          return;
        }
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadResource();
  }, [type, id]);

  if (loading) {
    return (
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <p className="text-lg text-gray-600">Cargando recurso...</p>
      </div>
    );
  }

  if (error) {
    return (
      <>
        <ErrorPopup 
          error={error} 
          onClose={() => setError(null)}
          redirectTo={`/resources/${type}`}
        />
      </>
    );
  }

  if (!resource) {
    return (
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <p className="text-lg text-gray-600">No se encontró el recurso solicitado</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-6">
      <div className="max-w-5xl mx-auto">
        {/* Main Title */}
        <h2 className="text-3xl font-serif italic font-bold text-primary-blue-strong mb-4">
          {parseColor(resource.mainTitle, "text-secondary-cyan-strong")}
        </h2>

        {/* Description */}
        <div className="prose prose-lg max-w-none mb-8 text-primary-blue-strong leading-relaxed">
          {parseRichText(resource.description, "text-primary-blue-strong font-semibold")}
        </div>

        {/* Data Sources */}
        <div className="mb-10">
          <ResourceDataSourcesList resourceType={type} resourceId={id} />
        </div>

        {/* Resource Display */}
        <div className="mt-12">
          <ResourceDisplay
            type={type}
            {...resource}
          />
        </div>
      </div>
    </div>
  );
}