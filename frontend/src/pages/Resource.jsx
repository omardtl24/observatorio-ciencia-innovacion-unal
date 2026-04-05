import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ResourceDisplay from "../components/ResourceDisplay";
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
      redirectToLogin(navigate);
      return;
    }

    if (!type || !id) {
      setError("Resource type and ID are required");
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
          redirectToLogin(navigate);
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
        <p className="text-lg text-gray-600">Loading resource...</p>
      </div>
    );
  }

  if (error) {
    return (
      <>
        <div className="min-h-screen px-6 py-12 flex items-center justify-center">
          <p className="text-lg text-red-600">Error: {error}</p>
        </div>
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
        <p className="text-lg text-gray-600">Resource not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Main Title */}
        <h2 className="text-3xl font-ancizarItalic font-bold italic text-primary-blue-strong mb-4">
          {parseColor(resource.mainTitle, "text-primary-cyan-base")}
        </h2>

        {/* Description */}
        <div className="prose prose-lg max-w-none mb-8 text-gray-700 leading-relaxed">
          {parseRichText(resource.description, "text-primary-blue-strong")}
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