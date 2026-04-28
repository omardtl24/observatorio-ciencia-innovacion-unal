import { isPdfResource } from "./resourceModels";
import { fetchFileWithAuth } from "./resourcesServices";

function renderPdf(fileSrc, options = {}) {
  const height = options.isFullscreen ? "100%" : "600";

  return (
    <div className={options.isFullscreen ? "h-full w-full" : ""}>
      {fileSrc && (
        <embed
          src={fileSrc}
          type="application/pdf"
          width="100%"
          height={height}
        />
      )}
    </div>
  );
}

function renderVisor(fileSrc, options = {}) {
  const containerClassName = options.isFullscreen ? "w-full h-full" : "w-full h-[600px]";

  return (
    <div className={containerClassName}>
      {fileSrc && (
        <iframe
          src={fileSrc}
          title="Visor"
          width="100%"
          height="100%"
          frameBorder="0"
        />
      )}
    </div>
  );
}

function renderSimulator(fileSrc, options = {}) {
  const containerClassName = options.isFullscreen ? "w-full h-full" : "w-full h-[600px]";

  return (
    <div className={containerClassName}>
      {fileSrc && (
        <iframe
          src={fileSrc}
          title="Simulador"
          width="100%"
          height="100%"
          frameBorder="0"
        />
      )}
    </div>
  );
}

function renderUnsupported() {
  return (
    <div className="w-full h-[600px] flex items-center justify-center">
      <p className="text-lg text-gray-600">Este tipo de recurso no se puede mostrar aquí.</p>
    </div>
  );
}

// Meta function that centralizes scenario selection.
export function getDisplayableKind(type) {
  const normalizedType = String(type || "").toLowerCase();

  if (isPdfResource(type)) {
    return "pdf";
  }

  if (normalizedType === "visor") {
    return "visor";
  }

  if (normalizedType === "simulator" || normalizedType === "simulators") {
    return "simulator";
  }

  return "unsupported";
}

export function renderDisplayableContent(type, fileSrc, options = {}) {
  const kind = getDisplayableKind(type);

  if (kind === "pdf") {
    return renderPdf(fileSrc, options);
  }

  if (kind === "visor") {
    return renderVisor(fileSrc, options);
  }

  if (kind === "simulator") {
    return renderSimulator(fileSrc, options);
  }

  return renderUnsupported();
}

export async function loadDisplayableResource({
  displayableKind,
  type,
  id,
  resourceDisplayable,
}) {
  if (!resourceDisplayable) {
    return null;
  }

  if (displayableKind === "pdf") {
    const baseUrl = `${import.meta.env.VITE_API_URL}/file/download/${resourceDisplayable}`;
    const params = {
      resource: type,
      id,
      display: "true",
    };
    return fetchFileWithAuth(baseUrl, params);
  }

  if (displayableKind === "visor") {
    return resourceDisplayable;
  }

  if (displayableKind === "simulator") {
    return resourceDisplayable;
  }

  return null;
}
