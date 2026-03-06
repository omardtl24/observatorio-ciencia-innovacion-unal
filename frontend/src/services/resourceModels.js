const TYPE_ALIASES = {
  report: "report",
  reports: "report",
  visor: "visor",
  visors: "visor",
  simulator: "simulator",
  simulators: "simulator",
  document: "document_presentation",
  documents: "document_presentation",
  document_presentation: "document_presentation",
  documents_presentation: "document_presentation",
};

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

  if (normalizedType === "report" || normalizedType === "simulator" || normalizedType === "document_presentation") {
    return "pdf";
  }

  return (item?.type || "").toString().toLowerCase() || "unknown";
}

export function toResourceCardModel(resourceType, item) {
  const normalizedType = normalizeResourceType(resourceType);

  return {
    id: item?.id,
    mainTitle: item?.main_title || "",
    auxiliaryTitle: item?.auxiliary_title || "",
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
  } else if (normalizedType === "document_presentation") {
    resourceDisplayable = item?.file_id ?? null;
  } else if (normalizedType === "visor") {
    resourceDisplayable = item?.visor_url ?? null;
  }

  return {
    id: item?.id,
    mainTitle: item?.main_title || "",
    auxiliaryTitle: item?.auxiliary_title || "",
    description: item?.description || "",
    type: normalizedType,
    resourceType: inferMediaType(normalizedType, item),
    resourceDisplayable,
  };
}

export function isPdfResource(resourceType) {
  return ["report", "simulator", "document_presentation"].includes(normalizeResourceType(resourceType));
}
