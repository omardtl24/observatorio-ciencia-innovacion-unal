import { useEffect, useState } from "react";
import ResourceCard from "../components/ResourceCard";
import { fetchResources, parseResourcesForCards, fetchFileWithAuth } from "../services/resourcesServices";

export default function ResourceDisplay({
    id,
    type,
    resource_displayable,
    resource_type
}){
    const [fileSrc, setFileSrc] = useState(null);
    console.log(resource_type);
    useEffect(() => {
        if ((type.toLowerCase().includes("report") || resource_type.toLowerCase().includes("pdf")) && resource_displayable) {
            // NOTE: Resources with query parameters require special handling for auth
            const baseUrl = `${import.meta.env.VITE_API_URL}/file/download/${resource_displayable}`;
            const params = {
                resource: resource_type,
                id: id,
                display: "true"
            };
            fetchFileWithAuth(baseUrl, params).then(src => setFileSrc(src)).catch(err => console.error(err));
        } else if (type.toLowerCase().includes("bi")) {
            // NOTE: Resources with query parameters require special handling for auth
            const baseUrl = `${import.meta.env.VITE_API_URL}/file/download/${id}`;
            const params = {
                resource: resource_displayable,
                id: id,
                display: "true"
            };
            fetchFileWithAuth(baseUrl, params).then(src => setFileSrc(src)).catch(err => console.error(err));
        }
    }, [resource_displayable, resource_type, id, type]);
    
    if (type.toLowerCase().includes("report") || 
        resource_type.toLowerCase().includes("pdf")) {
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
        )
    }else if (type.toLowerCase().includes("bi")) {
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
        )
    } else {
        return (
            <div className="w-full h-[600px] flex items-center justify-center">
                <p className="text-lg text-gray-600">Resource type not supported for display.</p>
            </div>
        )
    }
}