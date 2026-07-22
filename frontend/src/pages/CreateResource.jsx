import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import ResourceCard from "../components/ResourceCard";
import {
  createResource,
  deleteFileById,
  fetchAssignableRoles,
  fetchDataSources,
  syncResourceDataSources,
  uploadResourceFile,
} from "../services/resourcesServices";
import { formatDate, hasAdministratorRole } from "../services/dashboardUtils";
import { parseColor, parseRichText } from "../services/stringServices.jsx";
import reportCoverImg from "../assets/cardImages/reports.png";
import reportHoveredCoverImg from "../assets/cardImages/reportsHover.png";
import visorCoverImg from "../assets/cardImages/visors.png";
import visorHoveredCoverImg from "../assets/cardImages/visorsHover.png";
import simulatorCoverImg from "../assets/cardImages/simulators.png";
import simulatorHoveredCoverImg from "../assets/cardImages/simulatorsHover.png";
import documentCoverImg from "../assets/cardImages/documents.png";
import documentHoveredCoverImg from "../assets/cardImages/documentsHover.png";
import reportIcon from "../assets/icons/resources/report-blue.svg";
import visorIcon from "../assets/icons/resources/visor-blue.svg";
import simulatorIcon from "../assets/icons/resources/simulator-blue.svg";
import documentIcon from "../assets/icons/resources/document-blue.svg";

const TYPE_ALIASES = {
  report: "report",
  reports: "report",
  document: "document",
  documents: "document",
  document_presentation: "document",
  documents_presentation: "document",
  documents_presentations: "document",
  simulator: "simulator",
  simulators: "simulator",
  visor: "visor",
  visors: "visor",
};

function normalizeResourceType(resourceType) {
  if (!resourceType) {
    return "report";
  }

  const key = String(resourceType).toLowerCase();
  return TYPE_ALIASES[key] || key;
}

const RESOURCE_DEFINITIONS = {
  report: {
    label: "Reporte",
    endpoint: "report",
    fileField: "document_file_id",
    fileLabel: "Archivo del reporte (PDF u otro)",
  },
  document: {
    label: "Documento o presentacion",
    endpoint: "document",
    fileField: "file_id",
    fileLabel: "Archivo del documento/presentacion",
  },
  simulator: {
    label: "Simulador",
    endpoint: "simulator",
    uploadField: "r_program",
    urlField: "simulator_url",
    fileLabel: "Archivo de la aplicacion (ZIP)",
  },
  visor: {
    label: "Visor",
    endpoint: "visor",
    uploadField: "r_program",
    urlField: "visor_url",
    fileLabel: "Archivo de la aplicacion (ZIP)",
  },
};

const RESOURCE_TYPES_WITH_DATA_SOURCES = new Set(["report", "visor", "simulator"]);

function supportsDataSources(type) {
  return RESOURCE_TYPES_WITH_DATA_SOURCES.has(type);
}

const INITIAL_FORM = {
  resourceType: "report",
  title: "",
  description: "",
  visor_url: "",
  simulator_url: "",
  from_file: true,
  file: null,
  role_ids: [],
  data_source_ids: [],
  updated_date: "",
};

const TYPE_SPANISH_LABELS = {
  report: "reporte",
  simulator: "simulador",
  visor: "visor",
  document: "documento",
};

const PREVIEW_ASSETS = {
  report: {
    coverImage: reportCoverImg,
    hoverCoverImage: reportHoveredCoverImg,
    icon: reportIcon,
  },
  simulator: {
    coverImage: simulatorCoverImg,
    hoverCoverImage: simulatorHoveredCoverImg,
    icon: simulatorIcon,
  },
  visor: {
    coverImage: visorCoverImg,
    hoverCoverImage: visorHoveredCoverImg,
    icon: visorIcon,
  },
  document: {
    coverImage: documentCoverImg,
    hoverCoverImage: documentHoveredCoverImg,
    icon: documentIcon,
  },
};

function getPlainFromHtml(html) {
  const container = document.createElement("div");
  container.innerHTML = html || "";
  return (container.innerText || "").replace(/\u00A0/g, " ");
}

function encodeMarkedFromHtml(html) {
  const container = document.createElement("div");
  container.innerHTML = html || "";

  const processNode = (node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.textContent || "";
    }

    if (node.nodeName === "BR") {
      return "\\n";
    }

    if (node.nodeType !== Node.ELEMENT_NODE) {
      return "";
    }

    const tagName = node.nodeName.toLowerCase();
    const childrenContent = Array.from(node.childNodes).map(processNode).join("");

    if (tagName === "strong" || tagName === "b") {
      return childrenContent ? `\\(${childrenContent}\\)` : "";
    }

    if (tagName === "div" || tagName === "p") {
      return `${childrenContent}\\n`;
    }

    return childrenContent;
  };

  return Array.from(container.childNodes)
    .map(processNode)
    .join("")
    .replace(/(?:\\n){3,}/g, "\\n\\n")
    .replace(/(?:\\n)+$/g, "");
}

function isSelectionInsideElement(selection, element) {
  if (!selection || !element || !selection.rangeCount) {
    return false;
  }

  const range = selection.getRangeAt(0);
  return element.contains(range.commonAncestorContainer);
}

function isShinyResource(resourceType) {
  const definition = RESOURCE_DEFINITIONS[resourceType];
  return Boolean(definition?.uploadField);
}

function toDateOnlyString(dateOnlyValue) {
  if (!dateOnlyValue) {
    return null;
  }

  return dateOnlyValue;
}

function getTodayDateOnly() {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 10);
}

export default function CreateResource() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState(INITIAL_FORM);
  const [richFields, setRichFields] = useState({
    title: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [rolesLoading, setRolesLoading] = useState(false);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [dataSourcesLoading, setDataSourcesLoading] = useState(false);
  const [availableDataSources, setAvailableDataSources] = useState([]);
  const [feedback, setFeedback] = useState({ type: "", message: "" });
  const [formatMessage, setFormatMessage] = useState("");
  const mainTitleRef = useRef(null);
  const descriptionRef = useRef(null);

  const currentDefinition = useMemo(
    () => RESOURCE_DEFINITIONS[form.resourceType],
    [form.resourceType]
  );

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const requestedType = normalizeResourceType(params.get("type"));
    if (!requestedType || !RESOURCE_DEFINITIONS[requestedType]) {
      return;
    }

    setForm((prev) => ({
      ...prev,
      resourceType: requestedType,
    }));
  }, [location.search]);

  useEffect(() => {
    let active = true;

    const loadRoles = async () => {
      setRolesLoading(true);
      try {
        const roles = await fetchAssignableRoles();
        if (!active) {
          return;
        }
        setAvailableRoles(Array.isArray(roles) ? roles : []);
      } catch {
        if (active) {
          setAvailableRoles([]);
        }
      } finally {
        if (active) {
          setRolesLoading(false);
        }
      }
    };

    loadRoles();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    const loadDataSources = async () => {
      setDataSourcesLoading(true);
      try {
        const dataSources = await fetchDataSources();
        if (!active) {
          return;
        }
        setAvailableDataSources(Array.isArray(dataSources) ? dataSources : []);
      } catch {
        if (active) {
          setAvailableDataSources([]);
        }
      } finally {
        if (active) {
          setDataSourcesLoading(false);
        }
      }
    };

    loadDataSources();

    return () => {
      active = false;
    };
  }, []);

  if (!isAuthenticated()) {
    redirectToLogin(navigate, "/resources/create");
    return null;
  }

  const user = getUserInfo();
  if (!hasAdministratorRole(user)) {
    return (
      <ErrorPopup
        error="Solo usuarios con rol Administrador pueden crear recursos."
        onClose={() => navigate("/")}
      />
    );
  }

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const setSourceMode = (fromFile) => {
    setForm((prev) => ({
      ...prev,
      from_file: fromFile,
      file: fromFile ? prev.file : null,
      [currentDefinition.urlField]: fromFile ? "" : prev[currentDefinition.urlField],
    }));

    if (fromFile) {
      updateField(currentDefinition.urlField, "");
    } else {
      updateField("file", null);
    }
  };

  const updateRichField = (field, value) => {
    setRichFields((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const toggleRoleSelection = (roleId) => {
    setForm((prev) => {
      const roleIds = Array.isArray(prev.role_ids) ? prev.role_ids : [];
      const alreadySelected = roleIds.includes(roleId);
      return {
        ...prev,
        role_ids: alreadySelected
          ? roleIds.filter((id) => id !== roleId)
          : [...roleIds, roleId],
      };
    });
  };

  const toggleDataSourceSelection = (dataSourceId) => {
    setForm((prev) => {
      const currentIds = Array.isArray(prev.data_source_ids) ? prev.data_source_ids : [];
      const alreadySelected = currentIds.includes(dataSourceId);
      return {
        ...prev,
        data_source_ids: alreadySelected
          ? currentIds.filter((id) => id !== dataSourceId)
          : [...currentIds, dataSourceId],
      };
    });
  };

  const applyHighlightFormat = (field, inputRef) => {
    const input = inputRef.current;
    if (!input) {
      return;
    }

    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !isSelectionInsideElement(selection, input)) {
      setFormatMessage("Selecciona el texto que deseas resaltar dentro del campo.");
      return;
    }

    document.execCommand("bold");
    updateRichField(field, input.innerHTML);
    setFormatMessage("Formato en negrilla aplicado.");

    requestAnimationFrame(() => {
      input.focus();
    });
  };

  const validate = () => {
    const mainTitle = getPlainFromHtml(richFields.title).trim();
    const description = getPlainFromHtml(richFields.description).trim();

    if (!mainTitle) {
      return "El campo Titulo principal es obligatorio";
    }

    if (form.resourceType === "visor") {
      if (!description) {
        return "La descripcion es obligatoria para visores";
      }
    }

    if (isShinyResource(form.resourceType)) {
      if (form.from_file) {
        if (!form.file) {
          return "Debes cargar un archivo ZIP antes de crear este recurso";
        }
      } else {
        const resourceUrl = (form[currentDefinition.urlField] || "").trim();
        if (!resourceUrl) {
          return "Debes indicar la URL del recurso";
        }
      }
    } else if (currentDefinition.fileField && !form.file) {
      return "Debes cargar un archivo antes de crear este recurso";
    }

    return null;
  };

  const buildPayload = (fileId) => {
    const encodedMainTitle = encodeMarkedFromHtml(richFields.title);
    const encodedDescription = encodeMarkedFromHtml(richFields.description);

    if (currentDefinition.uploadField && form.from_file) {
      const formData = new FormData();
      formData.append("title", encodedMainTitle.trim());
      formData.append("from_file", "true");

      if (encodedDescription.trim()) {
        formData.append("description", encodedDescription);
      }

      formData.append(currentDefinition.uploadField, form.file);

      if (Array.isArray(form.role_ids) && form.role_ids.length > 0) {
        form.role_ids.forEach((roleId) => {
          formData.append("role_ids", String(roleId));
        });
      }

      return formData;
    }

    const basePayload = {
      title: encodedMainTitle.trim(),
    };

    if (currentDefinition.uploadField) {
      basePayload.from_file = Boolean(form.from_file);
    }

    const normalizedUpdatedAt = toDateOnlyString(form.updated_date);
    if (normalizedUpdatedAt) {
      basePayload.updated_at = normalizedUpdatedAt;
    }

    if (encodedDescription.trim()) {
      basePayload.description = encodedDescription;
    }

    if (currentDefinition.urlField && !form.from_file) {
      basePayload[currentDefinition.urlField] = (form[currentDefinition.urlField] || "").trim();
    }

    if (currentDefinition.fileField && fileId) {
      basePayload[currentDefinition.fileField] = fileId;
    }

    if (Array.isArray(form.role_ids) && form.role_ids.length > 0) {
      basePayload.role_ids = form.role_ids;
    }

    return basePayload;
  };

  const previewUpdatedAt = form.updated_date
    ? formatDate(form.updated_date)
    : "No disponible";

  const previewMainTitle = getPlainFromHtml(richFields.title).trim() || "Titulo principal";
  const previewType = form.resourceType === "visor" || form.resourceType === "simulator" ? "ZIP" : "PDF";
  const previewMainTitleEncoded = encodeMarkedFromHtml(richFields.title).trim() || "Titulo principal";
  const previewDescriptionEncoded = encodeMarkedFromHtml(richFields.description).trim() ||
    "Aqui veras una vista previa de la descripcion del recurso.";
  const previewCardType = form.resourceType;
  const previewAssets = PREVIEW_ASSETS[form.resourceType] || PREVIEW_ASSETS.report;
  const previewSpanishType = TYPE_SPANISH_LABELS[form.resourceType] || "recurso";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });

    const validationError = validate();
    if (validationError) {
      setFeedback({ type: "error", message: validationError });
      return;
    }

    setSubmitting(true);
    let uploadedFileId = null;

    try {
      if (currentDefinition.uploadField && form.from_file) {
        // The ZIP is sent as the resource payload, so no pre-upload is needed.
      } else if (currentDefinition.fileField) {
        const uploadedFile = await uploadResourceFile(form.file);
        uploadedFileId = uploadedFile?.id;
        if (!uploadedFileId) {
          throw new Error("No se pudo obtener el id del archivo cargado");
        }
      }

      const payload = buildPayload(uploadedFileId);
      const createdResource = await createResource(
        currentDefinition.endpoint,
        payload,
        toDateOnlyString(form.updated_date)
      );

      if (supportsDataSources(currentDefinition.endpoint) && createdResource?.id) {
        await syncResourceDataSources(
          currentDefinition.endpoint,
          createdResource.id,
          form.data_source_ids
        );
      }
      navigate("/dashboard");
    } catch (error) {
      // If resource creation fails after file upload, rollback orphan file.
      if (uploadedFileId) {
        try {
          await deleteFileById(uploadedFileId);
        } catch {
          // Ignore rollback errors and keep original failure message.
        }
      }

      setFeedback({
        type: "error",
        message: error?.message || "No fue posible crear el recurso",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <div className="bg-white border border-gray-200 rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-semibold text-secondary-cyan-strong mb-2">Crear recurso</h1>
          <p className="text-gray-600 mb-8">
            Completa los campos obligatorios para el tipo de recurso seleccionado.
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
          <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
            Usa los botones para aplicar negrilla directamente en el texto.
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de recurso</label>
            <div className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50 text-gray-700">
              {currentDefinition.label}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between gap-2 mb-1">
              <label className="block text-sm font-medium text-gray-700">Titulo principal *</label>
              <button
                type="button"
                onClick={() => applyHighlightFormat("title", mainTitleRef)}
                className="border border-primary-blue text-primary-blue px-2.5 py-1 rounded text-xs font-semibold hover:bg-blue-50 transition"
              >
                Resaltar texto
              </button>
            </div>
            <div
              ref={mainTitleRef}
              contentEditable={!submitting}
              suppressContentEditableWarning
              onInput={(e) => updateRichField("title", e.currentTarget.innerHTML)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 min-h-10 whitespace-pre-wrap"
            />
          </div>

          <div>
            <div className="flex items-center justify-between gap-2 mb-1">
              <label className="block text-sm font-medium text-gray-700">Descripcion</label>
              <button
                type="button"
                onClick={() => applyHighlightFormat("description", descriptionRef)}
                className="border border-primary-blue text-primary-blue px-2.5 py-1 rounded text-xs font-semibold hover:bg-blue-50 transition"
              >
                Resaltar texto
              </button>
            </div>
            <div
              ref={descriptionRef}
              contentEditable={!submitting}
              suppressContentEditableWarning
              onInput={(e) => updateRichField("description", e.currentTarget.innerHTML)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 min-h-28 whitespace-pre-wrap"
            />
            <p className="text-xs text-gray-500 mt-1">Puedes usar Enter para agregar saltos de linea.</p>
          </div>

          {formatMessage && (
            <p className="text-xs text-blue-700 bg-blue-50 border border-blue-200 rounded px-3 py-2">
              {formatMessage}
            </p>
          )}

          {currentDefinition.uploadField && (
            <button
              type="button"
              role="switch"
              aria-checked={form.from_file}
              onClick={() => setSourceMode(!form.from_file)}
              disabled={submitting}
              className={`relative flex h-11 w-full items-center rounded-xl border border-gray-300 bg-primary-green-light p-1 transition-all duration-200 ${
                submitting ? "opacity-60 cursor-not-allowed" : "cursor-pointer"
              }`}
            >
              <span className="sr-only">Cambiar origen del recurso</span>

              {/* Indicador */}
              <span
                className={`absolute top-1 bottom-1 w-[calc(50%-0.25rem)] rounded-lg bg-white shadow transition-transform duration-200 ${
                  form.from_file
                    ? "translate-x-0"
                    : "translate-x-[calc(100%+0.25rem)]"
                }`}
              />

              {/* Opción ZIP */}
              <span
                className={`relative z-10 flex w-1/2 justify-center text-sm font-semibold transition-colors duration-200 ${
                  form.from_file ? "text-gray-900" : "text-gray-500"
                }`}
              >
                Archivo ZIP
              </span>

              {/* Opción URL */}
              <span
                className={`relative z-10 flex w-1/2 justify-center text-sm font-semibold transition-colors duration-200 ${
                  !form.from_file ? "text-gray-900" : "text-gray-500"
                }`}
              >
                URL directa
              </span>
            </button>
          )}

          {currentDefinition.uploadField && form.from_file && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {currentDefinition.fileLabel} *
              </label>
              <input
                type="file"
                onChange={(e) => updateField("file", e.target.files?.[0] || null)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                disabled={submitting}
              />
              <p className="text-xs text-gray-500 mt-1">
                Carga el ZIP de la aplicacion para construir el visor o simulador.
              </p>
            </div>
          )}

          {currentDefinition.uploadField && !form.from_file && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL directa del recurso *
              </label>
              <input
                type="url"
                value={form[currentDefinition.urlField]}
                onChange={(e) => updateField(currentDefinition.urlField, e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                placeholder="https://..."
                disabled={submitting}
              />
              <p className="text-xs text-gray-500 mt-1">
                Pega la URL directa del visor o simulador.
              </p>
            </div>
          )}

          {currentDefinition.fileField && !currentDefinition.uploadField && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {currentDefinition.fileLabel} *
              </label>
              <input
                type="file"
                onChange={(e) => updateField("file", e.target.files?.[0] || null)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                disabled={submitting}
              />
              {form.file && (
                <p className="text-xs text-gray-500 mt-1">
                  Archivo seleccionado: <strong>{form.file.name}</strong>
                </p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Roles con acceso
            </label>
            <p className="text-xs text-gray-500 mb-2">
              El rol Administrador se asigna por defecto y no se muestra aqui.
            </p>

            {rolesLoading && (
              <p className="text-sm text-gray-500">Cargando roles...</p>
            )}

            {!rolesLoading && availableRoles.length === 0 && (
              <p className="text-sm text-gray-500">No hay roles adicionales disponibles.</p>
            )}

            {!rolesLoading && availableRoles.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 rounded-lg border border-gray-200 p-3">
                {availableRoles.map((role) => {
                  const roleId = role?.id;
                  const isChecked = Array.isArray(form.role_ids) && form.role_ids.includes(roleId);
                  return (
                    <label key={roleId} className="flex items-center gap-2 text-sm text-gray-700">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleRoleSelection(roleId)}
                        disabled={submitting}
                      />
                      <span>{role?.name || "Rol sin nombre"}</span>
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          {supportsDataSources(form.resourceType) && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fuentes de datos asociadas
              </label>

              {dataSourcesLoading && (
                <p className="text-sm text-gray-500">Cargando fuentes de datos...</p>
              )}

              {!dataSourcesLoading && availableDataSources.length === 0 && (
                <p className="text-sm text-gray-500">No hay fuentes de datos disponibles.</p>
              )}

              {!dataSourcesLoading && availableDataSources.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 rounded-lg border border-gray-200 p-3">
                  {availableDataSources.map((dataSource) => {
                    const dataSourceId = dataSource?.id;
                    const isChecked = Array.isArray(form.data_source_ids)
                      && form.data_source_ids.includes(dataSourceId);
                    return (
                      <label key={dataSourceId} className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleDataSourceSelection(dataSourceId)}
                          disabled={submitting}
                        />
                        <span>{dataSource?.name || "Fuente de datos sin nombre"}</span>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de actualización personalizada (opcional)</label>
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={form.updated_date}
                onChange={(e) => updateField("updated_date", e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                disabled={submitting}
              />
              <button
                type="button"
                onClick={() => updateField("updated_date", getTodayDateOnly())}
                className="border border-primary-blue text-primary-blue px-3 py-2 rounded-lg text-xs font-semibold hover:bg-blue-50 transition"
                disabled={submitting}
              >
                Usar hoy
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">Al guardar, esta fecha se enviara con hora 00:00.</p>
          </div>

          {feedback.message && (
            <div
              className={`rounded-lg px-4 py-3 text-sm ${
                feedback.type === "success"
                  ? "bg-green-100 text-green-700 border border-green-200"
                  : "bg-red-100 text-red-700 border border-red-200"
              }`}
            >
              {feedback.message}
            </div>
          )}

          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="bg-secondary-cyan-strong text-white px-5 py-2.5 rounded-lg font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Creando..." : "Crear recurso"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="border border-gray-300 text-gray-700 px-5 py-2.5 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              Volver al dashboard
            </button>
          </div>
          </form>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl shadow-md p-8 lg:sticky lg:top-8">
          <h2 className="text-2xl font-semibold text-secondary-cyan-strong mb-1">Vista previa</h2>
          <p className="text-sm text-gray-600 mb-6">
            Asi se vera la tarjeta y el titulo en el detalle del recurso.
          </p>

          <div className="space-y-8">
            <div>
              <p className="text-sm text-gray-600 mb-3">Vista de tarjeta:</p>
              <div>
                <ResourceCard
                  id={0}
                  number={''}
                  mainTitle={previewMainTitle}
                  spanishResourceType={previewSpanishType}
                  type={previewType}
                  updatedAt={previewUpdatedAt}
                  resourceIcon={previewAssets.icon}
                  coverImage={previewAssets.coverImage}
                  hoverCoverImage={previewAssets.hoverCoverImage}
                  resourceType={previewCardType}
                  disableNavigation
                />
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-3">Vista del titulo en detalle:</p>
              <div className="rounded-xl border border-gray-200 bg-white p-4">
                <h2 className="text-3xl font-serif italic font-bold text-primary-blue-strong mb-1">
                  {parseColor(previewMainTitleEncoded, "text-secondary-cyan-base")}
                </h2>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-3">Vista de descripcion en detalle:</p>
              <div className="prose prose-lg max-w-none mb-8 text-primary-blue-strong leading-relaxed">
                {parseRichText(previewDescriptionEncoded, "text-primary-blue-strong")}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
