import { isPdfResource } from "./resourceModels";
import { fetchFileWithAuth } from "./resourcesServices";
import { useEffect, useState } from "react";
import { getToken } from "./authService";

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

function VisorFrame({ fileSrc, id, options = {} }) {
  const containerClassName = options.isFullscreen ? "w-full h-full" : "w-full h-[600px]";
  const [allowed, setAllowed] = useState(null);

  useEffect(() => {
    let active = true;
    const checkAccess = async () => {
      if (!id) {
        setAllowed(false);
        return;
      }
      try {
        const token = getToken();
        const apiUrl = import.meta.env.VITE_API_URL;
        const resp = await fetch(`${apiUrl}/access/visor/${id}`, {
          method: "GET",
          credentials: "include",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!active) return;
        setAllowed(resp.ok);
      } catch (err) {
        if (!active) return;
        setAllowed(false);
      }
    };

    checkAccess();
    return () => {
      active = false;
    };
  }, [id]);

  return (
    <div className={containerClassName}>
      {allowed === null && <div />}
      {allowed === true && fileSrc && (
        <iframe src={fileSrc} title="Visor" width="100%" height="100%" frameBorder="0" />
      )}
      {allowed === false && (
        <div className="w-full h-[600px] flex items-center justify-center">
          <p className="text-lg text-gray-600">No tienes permiso para ver este visor.</p>
        </div>
      )}
    </div>
  );
}

function SimulatorFrame({ fileSrc, id, options = {} }) {
  const containerClassName = options.isFullscreen ? "w-full h-full" : "w-full h-[600px]";
  const [allowed, setAllowed] = useState(null);

  useEffect(() => {
    let active = true;
    const checkAccess = async () => {
      if (!id) {
        setAllowed(false);
        return;
      }
      try {
        const token = getToken();
        const apiUrl = import.meta.env.VITE_API_URL;
        const resp = await fetch(`${apiUrl}/access/simulator/${id}`, {
          method: "GET",
          credentials: "include",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!active) return;
        setAllowed(resp.ok);
      } catch (err) {
        if (!active) return;
        setAllowed(false);
      }
    };

    checkAccess();
    return () => {
      active = false;
    };
  }, [id]);

  return (
    <div className={containerClassName}>
      {allowed === null && <div />}
      {allowed === true && fileSrc && (
        <iframe src={fileSrc} title="Simulador" width="100%" height="100%" frameBorder="0" />
      )}
      {allowed === false && (
        <div className="w-full h-[600px] flex items-center justify-center">
          <p className="text-lg text-gray-600">No tienes permiso para ver este simulador.</p>
        </div>
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

export function renderDisplayableContent(type, fileSrc, options = {}, id = null) {
  const kind = getDisplayableKind(type);

  if (kind === "pdf") {
    return renderPdf(fileSrc, options);
  }

  if (kind === "visor") {
    return <VisorFrame fileSrc={fileSrc} id={id} options={options} />;
  }

  if (kind === "simulator") {
    return <SimulatorFrame fileSrc={fileSrc} id={id} options={options} />;
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
