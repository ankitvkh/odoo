/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

// Models that should NOT use enhanced delete (blacklist)
// Add models here that you want to skip
const EXCLUDED_MODELS = [
    'ir.ui.menu',
    'ir.model',
    'ir.model.fields',
    // Add system models or models you want to exclude
];

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
    },

    async onDeleteSelectedRecords() {
        const selectedRecords = this.model.root.selection;
        if (selectedRecords.length === 0) {
            return;
        }

        const modelName = this.model.root.resModel;
        
        // Check if this model should be excluded from enhanced delete
        if (EXCLUDED_MODELS.includes(modelName)) {
            // Use default delete for excluded models
            return super.onDeleteSelectedRecords();
        }

        const recordIds = selectedRecords.map(record => record.resId);

        try {
            // Call our wizard creation method
            const wizardId = await this.orm.call(
                'enhanced.delete.confirm.wizard',
                'create_wizard',
                [recordIds, modelName]
            );

            // If wizard creation returns False, use default delete
            if (!wizardId) {
                return super.onDeleteSelectedRecords();
            }

            if (wizardId) {
                // Open the wizard
                const result = await this.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'enhanced.delete.confirm.wizard',
                    res_id: wizardId,
                    views: [[false, 'form']],
                    target: 'new',
                    context: this.model.root.context,
                });

                // Reload the list after wizard closes
                if (result) {
                    await this.model.root.load();
                }
                
                return result;
            }
        } catch (error) {
            console.error('Enhanced delete wizard failed:', error);
            // Fallback to normal delete
            return super.onDeleteSelectedRecords();
        }
    }
});

console.log("Enhanced Delete Confirm module loaded - All models enabled (except exclusions)");