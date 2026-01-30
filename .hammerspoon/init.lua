-- Base URL for all endpoints
local baseURL = "http://pizero.gnlc.lan:5000/api"

-- Mapping from Teams status to endpoint paths
local statusPaths = {
    ["Available"] = "/free",
    ["Busy"] = "/busy",
    ["Do not disturb"] = "/dnd",
    ["Away"] = "/away",
    ["Offline"] = "/off",
}

-- Store last known status
local lastStatus = nil

-- Function to send status to the corresponding API endpoint
local function sendStatusToAPI(status)
    local path = statusPaths[status]
    if not path then
        print("No endpoint defined for status:", status)
        return
    end

    local endpointURL = baseURL .. path

    -- Call endpoint using GET (browser-style)
    hs.http.asyncGet(endpointURL, nil, function(statusCode, responseBody, responseHeaders)
        print("Called endpoint for", status, "->", endpointURL, "Response:", statusCode)
    end)
end

-- Function to get Teams status using AX
local function getTeamsStatus()
    local app = hs.application.get("Microsoft Teams")
    if not app then return nil end

    local axApp = hs.axuielement.applicationElement(app)
    if not axApp then return nil end

    local function findStatus(element)
        local description = element:attributeValue("AXDescription")
        if description then
            if description:match("Available") then return "Available" end
            if description:match("Busy") then return "Busy" end
            if description:match("Do not disturb") then return "Do not disturb" end
            if description:match("Away") then return "Away" end
            if description:match("Offline") then return "Offline" end
        end

        local children = element:attributeValue("AXChildren")
        if children then
            for _, child in ipairs(children) do
                local result = findStatus(child)
                if result then return result end
            end
        end
        return nil
    end

    return findStatus(axApp)
end

-- Timer to check status every 2 seconds
hs.timer.doEvery(2, function()
    local status = getTeamsStatus()
    if status and status ~= lastStatus then
        print("Microsoft Teams status changed to:", status)
        lastStatus = status
        sendStatusToAPI(status)
    end
end)
