const TYPE_ALIASES = {
  report: "report",
  reports: "report",
  visor: "visor",
  visors: "visor",
  simulator: "simulator",
  simulators: "simulator",
  document: "document",
  documents: "document",
  document_presentation: "document",
  documents_presentation: "document",
  documents_presentations: "document",
};

const PRESENTATION_INFO = {
  visor: {
    title: "¡Accede a nuestros \\(visores interactivos\\)!",
    text: "Los visores son plataformas ingteractivas que facilitan la lectura de grandes volúmenes de información y muestran el impacto real de la Facultad de Ciencias a través de visualizaciones dinámicas e intuitivas. Estas herramientas permiten que investigadores, estudiantes y personal administrativo accedan a bases de datos institucionales, realicen análisis personalizados y generen métricas según las necesidades"
  },
  simulator: {
    title: "¡Accede a nuestros \\(simuladores\\)!",
    text: "Son herramientas interactivas que modelan escenarios institucionales y pronostican sus efectos sobre la comunidad universitaria.\nCon ellos, la Facultad de Ciencias puede anticipar resultados e identificar oportunidades de mejora para fortalecer la experiencia educativa. Además, contribuyen a la toma de decisiones basada en evidencia."
  },
  document: {
    title: "¡Accede a nuestros \\(documentos y presentaciones\\)!",
    text: "Otra forma que utiliza el Observatorio para presentar información relevante son los documentos digitales de texto y las presentaciones con diapositivas. Los documentos consignan procesos como la revisión de literatura y establecimiento de soportes académicos en los que se enmarcan las distintas actividades del Observatorio.\nPor otro lado, se elaboraron presentaciones visuales con el fin de comunicar, ante los actores correspondientes, los principales hallazgos y resultados para la toma de decisiones. En esta sección, usted podrá encontrar algunos de estos documentos."
  },
  report: {
    title: "¡Accede a nuestros \\(reportes\\)!",
    text: "Otra forma que utiliza el Observatorio para presentar información relevante son los documentos digitales de texto y las presentaciones con diapositivas. Los documentos consignan procesos como la revisión de literatura y establecimiento de soportes académicos en los que se enmarcan las distintas actividades del Observatorio.\nPor otro lado, se elaboraron presentaciones visuales con el fin de comunicar, ante los actores correspondientes, los principales hallazgos y resultados para la toma de decisiones. En esta sección, usted podrá encontrar algunos de estos documentos."
  }
}

function normalizeResourceType(resourceType) {
  if (!resourceType) return "report";
  const key = String(resourceType).toLowerCase();
  return TYPE_ALIASES[key] || key;
}

function normalizeDate(item) {
  return item?.updated_at || item?.created_at || null;
}

function inferMediaType(normalizedType, item) {
  if (normalizedType === "visor") {
    const rawType = (item?.type || "").toString().toLowerCase();
    if (rawType.includes("bi")) return "bi";
    return rawType || "visor_url";
  }

  if (normalizedType === "report" || normalizedType === "simulator" || normalizedType === "document") {
    return "pdf";
  }

  return (item?.type || "").toString().toLowerCase() || "unknown";
}

export function getPresentationInfo(resourceType) {
  const normalizedType = normalizeResourceType(resourceType);
  return PRESENTATION_INFO[normalizedType] || null;
}

export function toResourceCardModel(resourceType, item) {
  const normalizedType = normalizeResourceType(resourceType);

  return {
    id: item?.id,
    mainTitle: item?.title || "",
    description: item?.description || "",
    updatedAt: normalizeDate(item),
    type: inferMediaType(normalizedType, item).toUpperCase(),
    resourceType: normalizedType,
  };
}

export function toResourceDisplayModel(resourceType, item) {
  const normalizedType = normalizeResourceType(resourceType);

  let resourceDisplayable = null;
  if (normalizedType === "report") {
    resourceDisplayable = item?.document_file_id ?? null;
  } else if (normalizedType === "simulator") {
    resourceDisplayable = item?.specs_file_id ?? null;
  } else if (normalizedType === "document") {
    resourceDisplayable = item?.file_id ?? null;
  } else if (normalizedType === "visor") {
    resourceDisplayable = item?.visor_url ?? null;
  }

  return {
    id: item?.id,
    mainTitle: item?.title || "",
    description: item?.description || "",
    type: normalizedType,
    resourceType: inferMediaType(normalizedType, item),
    resourceDisplayable,
  };
}

export function isPdfResource(resourceType) {
  return ["report", "simulator", "document"].includes(normalizeResourceType(resourceType));
}
