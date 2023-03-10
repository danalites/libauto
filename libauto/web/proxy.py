import zipfile
from libauto.utils.user import getUserHome

manifest_json = """
{
"version": "1.0.0",
"manifest_version": 3,
"name": "Chrome Proxy",
"permissions": [
"proxy",
"tabs",
"unlimitedStorage",
"storage",
"<all_urls>",
"webRequest",
"webRequestBlocking"
],
"background": {
"service_worker": "background.js"
},
"Minimum_chrome_version":"76.0.0"
}
"""

background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
    }
};
chrome.proxy.settings.set({ value: config, scope: "regular" }, function () { });
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    { urls: ["<all_urls>"] },
    ['blocking']
);
"""


def chrome_proxy_plugin(proxy_text):
    host, port, user, pwd = proxy_text.split(":")
    plugin_file = getUserHome('proxy_auth_plugin.zip')
    content_js = background_js % (host, port, user, pwd)

    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", content_js)

    return plugin_file
