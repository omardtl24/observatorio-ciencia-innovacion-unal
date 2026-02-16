import { useEffect, useState } from "react";
import ResourceCard from "../components/ResourceCard";
import { fetchResources, parseResourcesForCards } from "../services/resourcesServices";

export default function ResourceDisplay({
    id,
    type,
    resource_displayable,
    resource_type
}){
    if (type.toLowerCase().includes("report") || 
        resource_type.toLowerCase().includes("pdf")) {
        return (
            <div>
                <embed
                    src={`${import.meta.env.VITE_API_URL}/file/download/${resource_displayable}?resource=${resource_type}&id=${id}&display=true`}
                    type="application/pdf"
                    width="100%"
                    height="600"
                />
            </div>
        )
    }else if (type.toLowerCase().includes("bi")) {
        return (
            <div className="w-full h-[600px]">
                <iframe
                    src={`${import.meta.env.VITE_API_URL}/file/download/${id}?resource=${resource_displayable}&id=${id}&display=true`}
                    title="BI Resource"
                    width="100%"
                    height="100%"
                    frameBorder="0"
                />
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