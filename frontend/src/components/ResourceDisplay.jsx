import { useEffect, useState } from "react";
import ResourceCard from "../components/ResourceCard";
import { fetchResources, parseResourcesForCards } from "../services/resourcesServices";

export default function ResourceDisplay({
    type,
    resource
}){
    if (type.lowerCase().contains("report")){
        return (
            <div>
                
            </div>
        )
    }
}