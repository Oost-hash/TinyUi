.pragma library

function pluginToActivate(item) {
    if (!item) {
        return "";
    }
    return item["pluginToActivate"] || "";
}

function connectPluginToActivateChanged(item, callback) {
    if (!item || !item["pluginToActivateChanged"]) {
        return;
    }
    item["pluginToActivateChanged"].connect(callback);
}
