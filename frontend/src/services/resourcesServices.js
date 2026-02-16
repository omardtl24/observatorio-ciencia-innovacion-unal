export async function fetchResources(type) {
    const fetch_url = `${import.meta.env.VITE_API_URL}/${type}/all`;
    const response = await fetch(fetch_url);
    if (!response.ok) {
        throw new Error(`Failed to fetch ${type} resources`);
    }
    return response.json();
}


export async function fetchResource(type, id) {
    const fetch_url = `${import.meta.env.VITE_API_URL}/${type}/${id}`;
    const response = await fetch(fetch_url);
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
    if (type==='report') resource = data.document_file_id
    console.log(data)
    console.log(type, resource)
    return {
        id: data.id,
        main_title: data.main_title,
        auxiliary_title: data.auxiliary_title,
        description: data.description,
        resource_type: data.type,
        type: type,
        resource_displayable: resource
    }
}