local http = require("resty.http")

local _M = {}

local DEFAULT_TIMEOUT_MS = 5000
local BACKEND_BASE_URL = os.getenv("NGINX_BACKEND_URL") or "http://backend:5000"
local ALLOWED_RESOURCE_TYPES = {
    simulator = true,
    visor = true,
}

local function trim_trailing_slash(value)
    return (value:gsub("/$", ""))
end

local function normalize_resource_id(resource_id)
    if not resource_id then
        return nil
    end

    local id = tostring(resource_id)
    if not ngx.re.match(id, [[^\d+$]], "jo") then
        return nil
    end

    return id
end

function _M.validate_access(resource_type, resource_id, jwt)
    if not ALLOWED_RESOURCE_TYPES[resource_type] then
        return false, ngx.HTTP_NOT_FOUND, "resource not found"
    end

    local normalized_id = normalize_resource_id(resource_id)
    if not normalized_id then
        return false, ngx.HTTP_NOT_FOUND, "resource not found"
    end

    if not jwt or jwt == "" then
        return false, ngx.HTTP_UNAUTHORIZED, "missing user_jwt cookie"
    end

    local httpc = http.new()
    httpc:set_timeout(DEFAULT_TIMEOUT_MS)

    local backend_url = string.format(
        "%s/access/%s/%s/",
        trim_trailing_slash(BACKEND_BASE_URL),
        resource_type,
        normalized_id
    )

    local response, request_err = httpc:request_uri(backend_url, {
        method = "GET",
        headers = {
            ["Authorization"] = "Bearer " .. jwt,
            ["Accept"] = "application/json",
        },
        keepalive = false,
    })

    if not response then
        ngx.log(ngx.ERR, "access validation request failed: ", request_err or "unknown error")
        return false, ngx.HTTP_BAD_GATEWAY, "authorization backend unavailable"
    end

    if response.status == ngx.HTTP_OK then
        return true
    end

    if response.status == ngx.HTTP_UNAUTHORIZED or response.status == ngx.HTTP_FORBIDDEN then
        return false, response.status, "access denied"
    end

    ngx.log(
        ngx.ERR,
        "unexpected authorization response: status=",
        response.status,
        " resource_type=",
        resource_type,
        " resource_id=",
        normalized_id
    )
    return false, ngx.HTTP_FORBIDDEN, "access denied"
end

return _M
