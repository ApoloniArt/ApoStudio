import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
    name: "ApoStudio.Display",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "ApoStudio_Display") return;

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            // Remove ALL existing display widgets by name
            if (this.widgets) {
                const pos = this.widgets.findIndex(w => w.name === "displaytext");
                if (pos !== -1) {
                    for (let i = pos; i < this.widgets.length; i++) {
                        this.widgets[i].onRemove?.();
                    }
                    this.widgets.length = pos;
                }
            }

            const text = Array.isArray(message?.text) ? message.text[0] : (message?.text ?? "");
            const w = ComfyWidgets["STRING"](this, "displaytext", ["STRING", { multiline: true }], app).widget;
            w.inputEl.readOnly = true;
            w.inputEl.style.opacity = 0.85;
            w.value = text;
        };
    },
});
