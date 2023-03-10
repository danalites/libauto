var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "185.199.229.156",
            port: parseInt(7492)
        },
        bypassList: ["foobar.com"]
    }
};

chrome.proxy.settings.set({ value: config, scope: "regular" }, function () { });
function callbackFn(details) {
    return {
        authCredentials: {
            username: "lrhrhnil",
            password: "3iu0982joqa2"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    { urls: ["<all_urls>"] },
    ['blocking']
);