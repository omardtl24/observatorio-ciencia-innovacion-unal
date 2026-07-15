import { fetchFromUrl, fetchResources } from "./resourcesServices";

const MONTH_NAMES_ES = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

export const RESOURCE_TABLES = [
  {
    key: "report",
    title: "Reportes",
    endpointCandidates: ["report"],
  },
  {
    key: "visor",
    title: "Visores",
    endpointCandidates: ["visor"],
  },
  {
    key: "simulator",
    title: "Simuladores",
    endpointCandidates: ["simulator"],
  },
  {
    key: "document",
    title: "Documentos y Presentaciones",
    endpointCandidates: ["document"],
  }
];

export const NON_RESOURCE_TABLES = [
  {
    key: "data_source",
    title: "Fuentes de Datos",
    endpointCandidates: ["data-source"],
  },
  {
    key: 'role',
    title: 'Roles',
    endpointCandidates: ['role'],
  }
]

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

  if (typeof value === "string") {
    const dateOnly = value.slice(0, 10);
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateOnly)) {
      const [year, month, day] = dateOnly.split("-");
      const monthName = MONTH_NAMES_ES[Number(month) - 1];
      if (monthName) {
        return `${Number(day)} de ${monthName} de ${year}`;
      }
    }
  }

  return "No disponible";
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

    if (typeof candidate === "string") {
      const dateOnly = candidate.slice(0, 10);
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateOnly)) {
        return dateOnly;
      }
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
    .sort((a, b) => String(b).localeCompare(String(a)))[0] || null;
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
