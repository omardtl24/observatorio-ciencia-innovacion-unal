import { fetchFromUrl, fetchResources } from "../services/resourcesServices";

export const RESOURCE_TABLES = [
  {
    key: "reports",
    title: "Reportes",
    endpointCandidates: ["report"],
  },
  {
    key: "visors",
    title: "Visores",
    endpointCandidates: ["visor"],
  },
  {
    key: "simulators",
    title: "Simuladores",
    endpointCandidates: ["simulator"],
  },
  {
    key: "documents_presentations",
    title: "Documentos y Presentaciones",
    endpointCandidates: ["documents_presentations"],
  },
];

export function hasAdministratorRole(user) {
  if (!user || !Array.isArray(user.roles)) {
    return false;
  }

  return user.roles.some((role) => {
    if (typeof role !== "string") {
      return false;
    }
    const normalized = role.trim().toLowerCase();
    return normalized === "administrador" || normalized === "admin" || normalized === "administrator";
  });
}

export function formatDate(value) {
  if (!value) {
    return "No disponible";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "No disponible";
  }

  return date.toLocaleDateString("es-CO", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function getItemLastUpdate(item) {
  if (!item || typeof item !== "object") {
    return null;
  }

  const candidates = [
    item.updated_at,
    item.updatedAt,
    item.last_update,
    item.lastUpdate,
    item.created_at,
    item.createdAt,
    item.date,
  ];

  for (const candidate of candidates) {
    if (!candidate) {
      continue;
    }

    const parsed = new Date(candidate);
    if (!Number.isNaN(parsed.getTime())) {
      return candidate;
    }
  }

  return null;
}

function hasAtLeastOneDate(items) {
  return items.some((item) => Boolean(getItemLastUpdate(item)));
}

export function getMostRecentDate(items) {
  return items
    .map((item) => getItemLastUpdate(item))
    .filter(Boolean)
    .sort((a, b) => new Date(b) - new Date(a))[0] || null;
}

export async function fetchFirstAvailableResource(endpointCandidates) {
  let lastError = null;

  for (const candidate of endpointCandidates) {
    try {
      const listData = await fetchResources(candidate);
      let normalizedData = Array.isArray(listData) ? listData : [];

      // Retry with full data when list payload does not include date fields.
      if (normalizedData.length > 0 && !hasAtLeastOneDate(normalizedData)) {
        const fullUrl = `${import.meta.env.VITE_API_URL}/${candidate}/all?full=true`;
        const fullData = await fetchFromUrl(fullUrl);
        if (Array.isArray(fullData) && fullData.length > 0) {
          normalizedData = fullData;
        }
      }

      return {
        data: normalizedData,
        error: null,
      };
    } catch (error) {
      lastError = error;
    }
  }

  return {
    data: [],
    endpoint: endpointCandidates[0],
    error: lastError,
  };
}
