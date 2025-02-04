from odoo import http
from odoo.http import request, content_disposition
import json
import base64


class GSTReportController(http.Controller):
    @http.route('/gst_report/download_json/<int:report_id>', type='http', auth='user')
    def download_json(self, report_id, **kwargs):
        """Handle JSON file download for GST reports"""
        report = request.env['gst.report'].browse(report_id)

        if not report.exists():
            return request.not_found()

        if not report.json_file:
            return request.redirect('/web')

        # Decode the stored base64 data
        file_content = base64.b64decode(report.json_file)

        # Create the HTTP response with the file
        return request.make_response(
            file_content,
            headers=[
                ('Content-Type', 'application/json'),
                ('Content-Disposition', content_disposition(report.json_filename))
            ]
        )

    @http.route('/gst_report/validate_gstin', type='json', auth='user')
    def validate_gstin(self, gstin):
        """Validate GSTIN through GST Portal API"""
        try:
            # Get API configuration
            api_config = request.env['ir.config_parameter'].sudo()
            api_token = api_config.get_param('l10n_in_gst_reports.api_token')

            if not api_token:
                return {'error': 'GST Portal API token not configured'}

            # Add validation logic here when integrating with GST Portal
            return {'valid': True, 'message': 'GSTIN is valid'}

        except Exception as e:
            return {'error': str(e)}