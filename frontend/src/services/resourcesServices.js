import { getToken } from "./authService";

export async function fetchFromUrl(url) {
    const token = getToken();
    const response = await fetch(url, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch from ${url}`);
    }
    return response.json();
}

export async function fetchFileWithAuth(url, additionalParams = {}) {
    const token = getToken();
    
    // Parse the URL to properly handle existing query params
    const urlObj = new URL(url, window.location.origin);
    
    // Add any additional parameters
    Object.entries(additionalParams).forEach(([key, value]) => {
        urlObj.searchParams.set(key, value);
    });
    
    const response = await fetch(urlObj.toString(), {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch file from ${url}`);
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}

export async function fetchResources(type) {
    const fetch_url = `${import.meta.env.VITE_API_URL}/${type}/all`;
    const token = getToken();
    const response = await fetch(fetch_url, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch ${type} resources`);
    }
    return response.json();
}


export async function fetchResource(type, id) {
    const fetch_url = `${import.meta.env.VITE_API_URL}/${type}/${id}`;
    const token = getToken();
    const response = await fetch(fetch_url, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch ${type} resource`);
    }
    return response.json();
}

export function parseResourcesForCards(type, data) {
    if (data.length === 0) return [];
    return data.map((item, index) => {
        return {
            id: item.id,
            main_title: item.main_title,
            auxiliar_title: item.auxiliary_title,
            description: item.description,
            update_at: item.updated_at,
            type: item.type,
            resource_type: type
        }
    })
}

export function parseResourcesText(type, data) {
    let resource = null;
    let resource_type = null;
    
    if (type==='report'){
        resource = data.document_file_id;
        resource_type = "report";
    }
    console.log(data)
    console.log(type, resource)
    return {
        id: data.id,
        main_title: data.main_title,
        auxiliary_title: data.auxiliary_title,
        description: data.description,
        resource_type: resource_type,
        type: type,
        resource_displayable: resource
    }
}