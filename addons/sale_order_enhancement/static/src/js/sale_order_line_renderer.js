/** @odoo-module **/

import { SaleOrderLineListRenderer } from "@sale/js/sale_order_line_field/sale_order_line_field";
import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";

patch(SaleOrderLineListRenderer.prototype, {
    getActiveColumns(list) {
        // Bypass ProductLabelSectionAndNoteListRender's getActiveColumns to keep the 'name' column
        let activeColumns = ListRenderer.prototype.getActiveColumns.call(this, list);
        
        // Ensure that the label/description is not rendered inside the product column cell
        list.records.forEach((record) => {
            record.columnIsProductAndLabel = false;
        });

        // Retain the standard SaleOrderLineListRenderer logic to filter out product_template_id
        // if product_id is also present.
        const productTmplCol = activeColumns.find((col) => col.name === 'product_template_id');
        const productCol = activeColumns.find((col) => col.name === 'product_id');
        if (productCol && productTmplCol) {
            activeColumns = activeColumns.filter((col) => col.name !== 'product_template_id');
        }

        // Restore this.titleField to 'name' because name is now a standalone column
        this.titleField = "name";

        return activeColumns;
    }
});
