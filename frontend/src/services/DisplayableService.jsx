import { isPdfResource } from "./resourceModels";

function renderPdf(fileSrc) {
  return (
    <div>
      {fileSrc && (
        <embed
          src={fileSrc}
          type="application/pdf"
          width="100%"
          height="600"
        />
      )}
    </div>
  );
}

function renderVisor(fileSrc) {
  return (
    <div className="w-full h-[600px]">
      {fileSrc && (
        <iframe
          src={fileSrc}
          title="BI Resource"
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
      <p className="text-lg text-gray-600">Resource type not supported for display.</p>
    </div>
  );
}

// Meta function that centralizes scenario selection.
export function getDisplayableKind(type) {
  if (isPdfResource(type)) {
    return "pdf";
  }

  if (type === "visor") {
    return "visor";
  }

  return "unsupported";
}

export function renderDisplayableContent(type, fileSrc) {
  const kind = getDisplayableKind(type);

  if (kind === "pdf") {
    return renderPdf(fileSrc);
  }

  if (kind === "visor") {
    return renderVisor(fileSrc);
  }

  return renderUnsupported();
}
