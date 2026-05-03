import { useEffect, useState } from "react";
import {
    getDisplayableKind,
    loadDisplayableResource,
    renderDisplayableContent,
} from "../services/DisplayableService";
import fullscreenIcon from "../assets/icons/fullscreen.png";

export default function ResourceDisplay({
    id,
    type,
    resourceDisplayable
}){
    const [fileSrc, setFileSrc] = useState(null);
    const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);
    const displayableKind = getDisplayableKind(type);
    const canShowFullscreen = ["pdf", "visor", "simulator"].includes(displayableKind) && Boolean(fileSrc);

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

    useEffect(() => {
        const handleEsc = (event) => {
            if (event.key === "Escape") {
                setIsFullscreenOpen(false);
            }
        };

        if (isFullscreenOpen) {
            window.addEventListener("keydown", handleEsc);
        }

        return () => {
            window.removeEventListener("keydown", handleEsc);
        };
    }, [isFullscreenOpen]);

    useEffect(() => {
        window.dispatchEvent(
            new CustomEvent("resource-fullscreen-visibility", {
                detail: { visible: isFullscreenOpen },
            })
        );

        return () => {
            window.dispatchEvent(
                new CustomEvent("resource-fullscreen-visibility", {
                    detail: { visible: false },
                })
            );
        };
    }, [isFullscreenOpen]);

    return (
        <>
            <div className="relative">
                {canShowFullscreen && (
                    <div className="absolute right-3 z-10">
                        <button
                            type="button"
                            onClick={() => setIsFullscreenOpen(true)}
                            className="flex items-center gap-2 rounded-md bg-white border border-primary-blue-strong px-3 py-2 text-md font-medium italic text-primary-blue-strong transition hover:bg-secondary-cyan-soft"
                        >
                            Ver en pantalla completa
                            <img 
                                src={fullscreenIcon} 
                                alt="Pantalla completa" 
                                className="w-6 h-6"
                            />
                        </button>
                    </div>
                )}
                {renderDisplayableContent(type, fileSrc, {}, id)}
            </div>

            {isFullscreenOpen && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
                    role="dialog"
                    aria-modal="true"
                    aria-label="Vista en pantalla completa"
                    onClick={() => setIsFullscreenOpen(false)}
                >
                    <div
                        className="relative h-[90vh] w-[95vw] overflow-hidden rounded-lg bg-white"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <button
                            type="button"
                            onClick={() => setIsFullscreenOpen(false)}
                            className="absolute right-3 top-3 z-10 rounded-md bg-white border border-primary-blue-strong px-3 py-2 text-md font-medium italic text-primary-blue-strong transition hover:bg-secondary-cyan-soft"
                        >
                            Cerrar
                        </button>
                        <div className="h-full w-full p-4 pt-16">
                            {renderDisplayableContent(type, fileSrc, { isFullscreen: true }, id)}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}