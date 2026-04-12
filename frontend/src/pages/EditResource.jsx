import { useEffect, useMemo, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ResourceCard from "../components/ResourceCard";
import {
  fetchResource,
  updateResource,
  updateResourceRoles,
  deleteFileById,
  fetchAssignableRoles,
  uploadResourceFile,
} from "../services/resourcesServices";
import { hasAdministratorRole } from "../services/dashboardUtils";
import { parseColor, parseRichText } from "../services/stringServices.jsx";

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
    fileField: "specs_file_id",
    fileLabel: "Archivo de especificaciones",
  },
  visor: {
    label: "Visor",
    endpoint: "visor",
    fileField: null,
    fileLabel: null,
  },
};

const INITIAL_FORM = {
  resourceType: "report",
  title: "",
  description: "",
  visor_type: "",
  visor_url: "",
  file: null,
  role_ids: [],
  updated_date: "",
};

const PREVIEW_IMAGES = {
  report: "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
  simulator: "https://images.unsplash.com/photo-1491895200222-0fc4a4c35e18?auto=format&fit=crop&w=800&q=80",
  visor: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=800&q=80",
  document: "https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=800&q=80",
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

function markedTextToEditableHtml(value) {
  if (!value || typeof value !== "string") {
    return "";
  }

  const escaped = value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return escaped
    .replace(/\\\((.*?)\\\)/g, "<strong>$1</strong>")
    .replace(/\\n|\n/g, "<br>");
}

function formatDateOnly(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 10);
}

function toMidnightISOString(dateOnlyValue) {
  if (!dateOnlyValue) {
    return null;
  }
  return `${dateOnlyValue}T00:00:00`;
}

function getTodayDateOnly() {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 10);
}

function isSelectionInsideElement(selection, element) {
  if (!selection || !element || !selection.rangeCount) {
    return false;
  }

  const range = selection.getRangeAt(0);
  return element.contains(range.commonAncestorContainer);
}

export default function EditResource() {
  const navigate = useNavigate();
  const { type, id } = useParams();
  const normalizedType = normalizeResourceType(type);
  const [form, setForm] = useState(INITIAL_FORM);
  const [richFields, setRichFields] = useState({
    title: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [rolesLoading, setRolesLoading] = useState(false);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [feedback, setFeedback] = useState({ type: "", message: "" });
  const [formatMessage, setFormatMessage] = useState("");
  const [existingFileId, setExistingFileId] = useState(null);
  const [existingFileName, setExistingFileName] = useState(null);
  const mainTitleRef = useRef(null);
  const descriptionRef = useRef(null);

  const currentDefinition = useMemo(
    () => RESOURCE_DEFINITIONS[form.resourceType],
    [form.resourceType]
  );

  useEffect(() => {
    if (mainTitleRef.current && mainTitleRef.current.innerHTML !== richFields.title) {
      mainTitleRef.current.innerHTML = richFields.title;
    }

    if (descriptionRef.current && descriptionRef.current.innerHTML !== richFields.description) {
      descriptionRef.current.innerHTML = richFields.description;
    }
  }, [richFields]);

  // Load resource data
  useEffect(() => {
    let active = true;

    const loadResource = async () => {
      if (!normalizedType || !id || !RESOURCE_DEFINITIONS[normalizedType]) {
        if (active) {
          setFeedback({ type: "error", message: "Tipo de recurso o ID inválido" });
          setLoading(false);
        }
        return;
      }

      try {
        const data = await fetchResource(normalizedType, id);
        if (!active) return;

        const parsedRoleIds = Array.isArray(data.role_ids)
          ? data.role_ids
          : Array.isArray(data.roles)
            ? data.roles
              .map((role) => {
                if (typeof role === "number") {
                  return role;
                }
                if (role && typeof role === "object") {
                  return role.id;
                }
                return null;
              })
              .filter((roleId) => typeof roleId === "number")
            : [];

        setForm((prev) => ({
          ...prev,
          resourceType: normalizedType,
          title: data.title || "",
          description: data.description || "",
          visor_type: data.type || "",
          visor_url: data.visor_url || "",
          role_ids: parsedRoleIds,
          updated_date: formatDateOnly(data.updated_at || data.updatedAt || data.last_update),
        }));

        setRichFields({
          title: markedTextToEditableHtml(data.title || ""),
          description: markedTextToEditableHtml(data.description || ""),
        });

        // Store existing file ID
        if (RESOURCE_DEFINITIONS[normalizedType].fileField) {
          const fileId = data[RESOURCE_DEFINITIONS[normalizedType].fileField];
          if (fileId) {
            setExistingFileId(fileId);
            // Extract filename from the data if available
            setExistingFileName(`Archivo actual: ${normalizedType}`);
          }
        }
      } catch (error) {
        if (active) {
          setFeedback({
            type: "error",
            message: error?.message || "No fue posible cargar el recurso",
          });
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadResource();

    return () => {
      active = false;
    };
  }, [normalizedType, id]);

  // Load roles
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

  if (!isAuthenticated()) {
    redirectToLogin(navigate, `/resource/${normalizedType}/${id}`, normalizedType);
    return null;
  }

  const user = getUserInfo();
  if (!hasAdministratorRole(user)) {
    return (
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <div className="w-full max-w-xl bg-white border border-gray-200 rounded-xl shadow-md p-8 text-center">
          <h1 className="text-2xl font-semibold text-primary-cyan-strong mb-2">Permisos insuficientes</h1>
          <p className="text-gray-700">
            Solo usuarios con rol Administrador pueden editar recursos.
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen px-6 py-12 flex items-center justify-center">
        <p className="text-lg text-gray-600">Cargando recurso...</p>
      </div>
    );
  }

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
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

  const applyHighlightFormat = (field, inputRef) => {
    const input = inputRef.current;
    if (!input) {
      return;
    }

    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !isSelectionInsideElement(selection, input)) {
      setFormatMessage("Selecciona un texto dentro del campo para aplicar negrilla.");
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
      if (!form.visor_type.trim()) {
        return "El tipo es obligatorio para visores";
      }
      if (!form.visor_url.trim()) {
        return "La URL es obligatoria para visores";
      }
    }

    if (currentDefinition.fileField && !form.file && !existingFileId) {
      return "Debes cargar un archivo para este recurso";
    }

    return null;
  };

  const buildPayload = (fileId) => {
    const encodedMainTitle = encodeMarkedFromHtml(richFields.title);
    const encodedDescription = encodeMarkedFromHtml(richFields.description);

    const basePayload = {
      title: encodedMainTitle.trim(),
    };

    const normalizedUpdatedAt = toMidnightISOString(form.updated_date);
    if (normalizedUpdatedAt) {
      basePayload.updated_at = normalizedUpdatedAt;
    }

    if (encodedDescription.trim()) {
      basePayload.description = encodedDescription;
    }

    if (form.resourceType === "visor") {
      basePayload.type = form.visor_type.trim();
      basePayload.visor_url = form.visor_url.trim();
    }

    if (currentDefinition.fileField && fileId) {
      basePayload[currentDefinition.fileField] = fileId;
    }

    return basePayload;
  };

  const previewUpdatedAt = form.updated_date
    ? new Date(`${form.updated_date}T00:00:00`).toLocaleDateString("es-CO", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
    : "No disponible";

  const previewMainTitle = getPlainFromHtml(richFields.title).trim() || "Titulo principal";
  const previewType = form.resourceType === "visor"
    ? (form.visor_type.trim() || "VISOR")
    : "PDF";
  const previewMainTitleEncoded = encodeMarkedFromHtml(richFields.title).trim() || "Titulo principal";
  const previewDescriptionEncoded = encodeMarkedFromHtml(richFields.description).trim() ||
    "Aqui veras una vista previa de la descripcion del recurso.";
  const previewCardType = form.resourceType;
  const previewCoverImage = PREVIEW_IMAGES[form.resourceType] || PREVIEW_IMAGES.report;

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
      // Upload new file if provided
      if (currentDefinition.fileField && form.file) {
        const uploadedFile = await uploadResourceFile(form.file);
        uploadedFileId = uploadedFile?.id;
        if (!uploadedFileId) {
          throw new Error("No se pudo obtener el id del archivo cargado");
        }
      }

      // Build payload with new file ID or existing one
      const fileIdToUse = uploadedFileId || existingFileId;
      const payload = buildPayload(fileIdToUse);

      // 1) Update base resource fields.
      await updateResource(currentDefinition.endpoint, id, payload, toMidnightISOString(form.updated_date));

      // 2) Update resource roles in a dedicated request.
      await updateResourceRoles(currentDefinition.endpoint, id, form.role_ids);

      navigate("/dashboard");
    } catch (error) {
      // If resource update fails after file upload, rollback orphan file.
      if (uploadedFileId) {
        try {
          await deleteFileById(uploadedFileId);
        } catch {
          // Ignore rollback errors and keep original failure message.
        }
      }

      setFeedback({
        type: "error",
        message: error?.message || "No fue posible actualizar el recurso",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <div className="bg-white border border-gray-200 rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-semibold text-primary-cyan-strong mb-2">Editar recurso</h1>
          <p className="text-gray-600 mb-8">
            Actualiza los campos necesarios para modificar este recurso.
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

          {form.resourceType === "visor" && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de visor *</label>
                <input
                  type="text"
                  value={form.visor_type}
                  onChange={(e) => updateField("visor_type", e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  disabled={submitting}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL del visor *</label>
                <input
                  type="url"
                  value={form.visor_url}
                  onChange={(e) => updateField("visor_url", e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  disabled={submitting}
                />
              </div>
            </>
          )}

          {currentDefinition.fileField && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {currentDefinition.fileLabel} (Opcional)
              </label>
              {existingFileName && (
                <p className="text-xs text-gray-600 mb-2">{existingFileName}</p>
              )}
              <input
                type="file"
                onChange={(e) => updateField("file", e.target.files?.[0] || null)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                disabled={submitting}
              />
              <p className="text-xs text-gray-500 mt-1">
                Carga un nuevo archivo si deseas reemplazar el actual.
              </p>
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
              className="bg-primary-cyan-strong text-white px-5 py-2.5 rounded-lg font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Actualizando..." : "Actualizar recurso"}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/resource/${normalizedType}/${id}`)}
              className="border border-gray-300 text-gray-700 px-5 py-2.5 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              Cancelar
            </button>
          </div>
          </form>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl shadow-md p-8 lg:sticky lg:top-8">
          <h2 className="text-2xl font-semibold text-primary-cyan-strong mb-1">Vista previa</h2>
          <p className="text-sm text-gray-600 mb-6">
            Asi se vera la tarjeta y el titulo en el detalle del recurso.
          </p>

          <div className="space-y-8">
            <div>
              <p className="text-sm text-gray-600 mb-3">Vista de tarjeta:</p>
              <div className="pointer-events-none">
                <ResourceCard
                  id={0}
                  mainTitle={previewMainTitle}
                  type={previewType}
                  updatedAt={previewUpdatedAt}
                  coverImage={previewCoverImage}
                  resourceType={previewCardType}
                />
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-3">Vista del titulo en detalle:</p>
              <div className="rounded-xl border border-gray-200 bg-white p-4">
                <h2 className="text-3xl font-serif italic font-bold text-primary-blue-strong mb-1">
                  {parseColor(previewMainTitleEncoded, "text-primary-cyan-base")}
                </h2>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-3">Vista de descripcion en detalle:</p>
              <div className="prose prose-lg max-w-none mb-8 text-gray-700 leading-relaxed">
                {parseRichText(previewDescriptionEncoded, "text-primary-blue-strong")}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
