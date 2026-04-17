import { useEffect, useState } from "react";
import { fetchResourceDataSources, fetchFromUrl } from "../services/resourcesServices";

export default function ResourceDataSourcesList({ 
  resourceType, 
  resourceId, 
  className = "" 
}) {
  const [dataSources, setDataSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [canDisplay, setCanDisplay] = useState(false);
  const [fileNames, setFileNames] = useState({});
  const [expandedDataSourceId, setExpandedDataSourceId] = useState(null);

  console.log("Entered", resourceType, resourceId);

  useEffect(() => {
    if (!resourceType || !resourceId) {
      setLoading(false);
      setCanDisplay(false);
      return;
    }

    const loadDataSources = async () => {
      try {
        setLoading(true);
        const data = await fetchResourceDataSources(resourceType, resourceId);
        const resourceDataSources = Array.isArray(data) ? data : [];

        if (resourceDataSources.length === 0) {
          setDataSources([]);
          setFileNames({});
          setCanDisplay(false);
          return;
        }

        const permissionChecks = await Promise.all(
          resourceDataSources.map(async (dataSource) => {
            try {
              await fetchFromUrl(`${import.meta.env.VITE_API_URL}/data-source/${dataSource.id}`);
              return true;
            } catch {
              return false;
            }
          })
        );

        if (permissionChecks.some((allowed) => !allowed)) {
          setDataSources([]);
          setFileNames({});
          setCanDisplay(false);
          return;
        }

        const names = {};
        await Promise.all(
          resourceDataSources.map(async (dataSource) => {
            if (!dataSource.file_id) {
              names[dataSource.id] = null;
              return;
            }

            try {
              const fileMetadata = await fetchFromUrl(
                `${import.meta.env.VITE_API_URL}/file/metadata/${dataSource.file_id}`
              );
              names[dataSource.id] = fileMetadata.filename || null;
            } catch {
              names[dataSource.id] = null;
            }
          })
        );

        setDataSources(resourceDataSources);
        setFileNames(names);
        setCanDisplay(true);
      } catch (err) {
        setDataSources([]);
        setFileNames({});
        setCanDisplay(false);
      } finally {
        setLoading(false);
      }
    };

    loadDataSources();
  }, [resourceType, resourceId]);

  const handleDownload = (dataSource) => {
    if (!dataSource.file_id) {
      return;
    }

    // Direct download using file API endpoint
    const downloadUrl = `${import.meta.env.VITE_API_URL}/file/download/${dataSource.file_id}`;
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.setAttribute("download", fileNames[dataSource.id] || `data-source-${dataSource.id}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleDetails = (dataSourceId) => {
    setExpandedDataSourceId((current) => (current === dataSourceId ? null : dataSourceId));
  };

  if (!resourceType || !resourceId) {
    return null;
  }

  if (loading) {
    return null;
  }

  if (!canDisplay || dataSources.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <h4 className="text-sm font-semibold text-gray-700">Fuentes de datos asociadas</h4>
      <div className="space-y-2">
        {dataSources.map((dataSource) => (
          <div
            key={dataSource.id}
            className="rounded-lg border border-gray-200 bg-white p-3 hover:bg-gray-50 transition"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {dataSource.name || "Sin nombre"}
                </p>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => handleDownload(dataSource)}
                  disabled={!dataSource.file_id}
                  className="inline-flex items-center justify-center rounded-lg border border-primary-blue text-primary-blue hover:bg-blue-50 px-2 py-1 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Descargar fuente de datos"
                  aria-label="Descargar fuente de datos"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className="w-4 h-4"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 14.899A7 7 0 1 1 15.71 8m-6.85 11m7-9-7 7m7 0-7-7" />
                  </svg>
                </button>

                <button
                  onClick={() => toggleDetails(dataSource.id)}
                  className="inline-flex items-center justify-center rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 px-2 py-1 transition"
                  title="Ver más detalles de la fuente de datos"
                  aria-label="Ver más detalles de la fuente de datos"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className="w-4 h-4"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5 12h14" />
                  </svg>
                </button>
              </div>
            </div>

            {expandedDataSourceId === dataSource.id && (
              <div className="mt-3 rounded-md bg-gray-50 border border-gray-200 p-3 text-xs text-gray-600 space-y-1">
                {fileNames[dataSource.id] ? (
                  <p>
                    Archivo: <span className="font-medium text-gray-800">{fileNames[dataSource.id]}</span>
                  </p>
                ) : (
                  <p>No tiene archivo asociado.</p>
                )}
                {dataSource.description && <p>{dataSource.description}</p>}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
