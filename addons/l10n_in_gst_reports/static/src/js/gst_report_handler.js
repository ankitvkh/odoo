/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { download } from "@web/core/network/download";

export class GSTReportHandler extends Component {
    setup() {
        // Initialize required services
        this.orm = useService("orm");          // For backend communication
        this.action = useService("action");     // For action management
        this.notification = useService("notification"); // For user notifications
    }

    /**
     * Handle report generation with progress updates
     */
    async generateReport() {
        try {
            const reportId = this.props.record.data.id;

            // Show progress notification
            this.notification.add(this.env._t("Generating report..."), {
                type: "info",
                sticky: true,
                className: "o_loading_notification",
            });

            // Call the backend method
            const result = await this.orm.call(
                "gst.report",
                "action_generate_report",
                [reportId]
            );

            // Remove progress notification
            this.notification.remove("o_loading_notification");

            if (result) {
                // Show success message
                this.notification.add(this.env._t("Report generated successfully"), {
                    type: "success"
                });

                // Reload the view to show updated data
                await this.action.doAction({
                    type: "ir.actions.client",
                    tag: "reload",
                });
            }
        } catch (error) {
            this.notification.add(error.message, {
                type: "danger"
            });
        }
    }

    /**
     * Handle JSON file download
     */
    async downloadJSON() {
        try {
            const reportId = this.props.record.data.id;

            // Trigger file download
            download({
                url: '/web/content',
                data: {
                    model: 'gst.report',
                    id: reportId,
                    field: 'json_file',
                    filename_field: 'json_filename',
                    download: true
                }
            });
        } catch (error) {
            this.notification.add(error.message, {
                type: "danger"
            });
        }
    }

    /**
     * Validate report data before generation
     */
    async validateData() {
        try {
            const reportId = this.props.record.data.id;

            const result = await this.orm.call(
                "gst.report",
                "_validate_report_period",
                [reportId]
            );

            // Show validation result
            this.notification.add(result.message, {
                type: result.status
            });

            return result.valid;
        } catch (error) {
            this.notification.add(error.message, {
                type: "danger"
            });
            return false;
        }
    }
}

// Register the component
GSTReportHandler.template = "l10n_in_gst_reports.GSTReportHandler";
registry.category("actions").add("gst_report_handler", GSTReportHandler);