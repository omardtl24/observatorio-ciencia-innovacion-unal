import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ResourceDisplay from "../components/ResourceDisplay";
import { fetchResource, parseResourcesText } from "../services/resourcesServices";
import { parseRichText } from "../services/stringServices.jsx";
export default function Resource() {
  const { type, id } = useParams();
  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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
        setError(err.message + " Please try again later.");
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
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <p className="text-lg text-red-600">Error: {error}</p>
      </div>
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
        <h1 className="text-4xl font-bold text-primary-cyan-strong mb-2">
          {resource.main_title}
        </h1>

        {/* Auxiliary Title */}
        <h2 className="text-2xl font-semibold text-primary-blue-strong mb-6">
          {resource.auxiliary_title}
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