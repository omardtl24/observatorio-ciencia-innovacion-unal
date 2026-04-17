import { useEffect, useState } from "react";
import { fetchResourceDataSources, fetchFromUrl, fetchFileWithAuth } from "../services/resourcesServices";

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
  const [isModalOpen, setIsModalOpen] = useState(false);

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

  const handleDownload = async (dataSource) => {
    if (!dataSource.file_id) {
      return;
    }

    try {
      const downloadUrl = `${import.meta.env.VITE_API_URL}/file/download/${dataSource.file_id}`;
      const objectUrl = await fetchFileWithAuth(downloadUrl, {
        resource: resourceType,
        id: resourceId,
        display: "true",
        data_source_id: dataSource.id,
      });

      const link = document.createElement("a");
      link.href = objectUrl;
      link.setAttribute("download", fileNames[dataSource.id] || `data-source-${dataSource.id}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
    } catch {
      // Silent fail to avoid breaking the UI flow.
    }
  };

  const toggleDetails = (dataSourceId) => {
    setExpandedDataSourceId((current) => (current === dataSourceId ? null : dataSourceId));
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setExpandedDataSourceId(null);
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
    <div className={className}>
      <button
        type="button"
        onClick={() => setIsModalOpen(true)}
        className="inline-flex items-center justify-center rounded-lg border bg-primary-blue-base px-3 py-2 text-sm font-semibold text-white transition hover:border-primary-blue-strong hover:bg-white hover:text-primary-blue-strong"
      >
        Ver fuentes de datos
      </button>

      {isModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Fuentes de datos asociadas"
          onClick={closeModal}
        >
          <div
            className="max-h-[85vh] w-full max-w-2xl overflow-hidden rounded-xl bg-white shadow-xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
              <h4 className="text-base font-semibold text-gray-800">Fuentes de datos asociadas</h4>
              <button
                type="button"
                onClick={closeModal}
                className="rounded-md px-2 py-1 text-sm text-white border border-primary-blue-base bg-primary-blue-strong transition hover:border-primary-blue-strong hover:bg-white hover:text-primary-blue-strong"
                aria-label="Cerrar fuentes de datos"
                title="Cerrar"
              >
                Cerrar
              </button>
            </div>

            <div className="max-h-[calc(85vh-65px)] space-y-2 overflow-y-auto p-4">
              {dataSources.map((dataSource) => (
                <div
                  key={dataSource.id}
                  className="rounded-lg border border-secondary-gray-soft bg-white p-3 hover:bg-secondary-gray-soft transition"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {dataSource.name || "Sin nombre"}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      <button
                        type="button"
                        onClick={() => handleDownload(dataSource)}
                        disabled={!dataSource.file_id}
                        className="inline-flex items-center justify-center rounded-lg border px-2 py-1 transition disabled:cursor-not-allowed disabled:border-gray-300 bg-primary-green-strong text-white hover:bg-primary-green-soft hover:border-primary-green-strong hover:text-black"
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
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v10m0 0-4-4m4 4 4-4M5 20h14" />
                        </svg>
                      </button>

                      <button
                        type="button"
                        onClick={() => toggleDetails(dataSource.id)}
                        className="inline-flex items-center justify-center rounded-lg border px-2 py-1 bg-primary-blue-base text-white hover:bg-primary-blue-soft hover:border-primary-blue-strong hover:text-black"
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
                      {dataSource.description ? <p>{dataSource.description}</p> : <p>Sin descripcion.</p>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
