import { useEffect, useState } from "react";
import {
    getDisplayableKind,
    loadDisplayableResource,
    renderDisplayableContent,
} from "../services/DisplayableService";

export default function ResourceDisplay({
    id,
    type,
    resourceDisplayable
}){
    const [fileSrc, setFileSrc] = useState(null);
    const displayableKind = getDisplayableKind(type);

    useEffect(() => {
        let active = true;
        let objectUrl = null;

        const loadResource = async () => {
            try {
                const src = await loadDisplayableResource({
                    displayableKind,
                    type,
                    id,
                    resourceDisplayable,
                });

                if (active) {
                    if (displayableKind === "pdf") {
                        objectUrl = src;
                    }
                    setFileSrc(src);
                }
            } catch (err) {
                if (active) {
                    setFileSrc(null);
                }
            }
        };

        loadResource();

        return () => {
            active = false;
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [resourceDisplayable, id, type, displayableKind]);

    return renderDisplayableContent(type, fileSrc);
}