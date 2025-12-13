/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";

export class EnhancedDeleteListController extends ListController {
    async onDeleteSelectedRecords() {
        const selectedRecords = this.model.root.selection;
        if (selectedRecords.length === 0) {
            return;
        }

        // Check if records have linked data
        const recordIds = selectedRecords.map(record => record.resId);
        const modelName = this.model.root.resModel;

        try {
            // Call our wizard creation method
            const result = await this.orm.call(
                'enhanced.delete.wizard',
                'create_wizard',
                [recordIds, modelName]
            );

            if (result) {
                // Open the wizard
                return this.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'enhanced.delete.wizard',
                    res_id: result,
                    views: [[false, 'form']],
                    target: 'new',
                    context: {
                        'delete_record_ids': recordIds,
                        'delete_model': modelName,
                    },
                });
            }
        } catch (error) {
            // If wizard creation fails (no linked records), proceed with normal delete
            if (error.message.includes('No linked records')) {
                return super.onDeleteSelectedRecords();
            }
            throw error;
        }

        // Fallback to normal delete
        return super.onDeleteSelectedRecords();
    }
}

registry.category("views").add("list", {
    ...listView,
    Controller: EnhancedDeleteListController,
});