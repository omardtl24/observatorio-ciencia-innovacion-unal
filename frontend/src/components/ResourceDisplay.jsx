import { useEffect, useState } from "react";
import { fetchFileWithAuth } from "../services/resourcesServices";
import { getDisplayableKind, renderDisplayableContent } from "../services/DisplayableService";

export default function ResourceDisplay({
    id,
    type,
    resource_displayable,
    resource_type
}){
    const [fileSrc, setFileSrc] = useState(null);
    const displayableKind = getDisplayableKind(type);

    useEffect(() => {
        let active = true;
        let objectUrl = null;

        const loadDisplayableResource = async () => {
            if (!resource_displayable) {
                setFileSrc(null);
                return;
            }

            try {
                if (displayableKind === "pdf") {
                    const baseUrl = `${import.meta.env.VITE_API_URL}/file/download/${resource_displayable}`;
                    const params = {
                        resource: type,
                        id,
                        display: "true",
                    };
                    const src = await fetchFileWithAuth(baseUrl, params);
                    if (active) {
                        objectUrl = src;
                        setFileSrc(src);
                    }
                    return;
                }

                if (displayableKind === "visor") {
                    setFileSrc(resource_displayable);
                }
            } catch (err) {
                if (active) {
                    setFileSrc(null);
                }
            }
        };

        loadDisplayableResource();

        return () => {
            active = false;
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [resource_displayable, resource_type, id, type, displayableKind]);

    return renderDisplayableContent(type, fileSrc);
}