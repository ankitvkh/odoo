# -*- coding: utf-8 -*-

from odoo import models, api, _
import logging
import io
import base64
from odoo.tools.pdf import PdfFileReader

_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _add_pages_to_writer(self, writer, document, prefix=None):
        """
        Override to skip orphan/broken PDF documents instead of crashing.
        """
        if not document:
            _logger.warning("[ORPHAN RECORD] Skipping document with no data. Prefix: %s", prefix)
            return

        try:
            # Try to read the PDF to verify it's valid
            reader = PdfFileReader(io.BytesIO(document), strict=False)
            # If it's a valid PDF, call super
            return super(IrActionsReport, self)._add_pages_to_writer(writer, document, prefix=prefix)
        except Exception as e:
            # Try to extract more info from prefix if possible (e.g. sol_id_123)
            record_info = ""
            if prefix:
                if 'sol_id_' in prefix:
                    sol_id = prefix.split('sol_id_')[1].split('_')[0]
                    record_info = f" (Linked to Sale Order Line ID: {sol_id})"
                elif 'quotation_document_id_' in prefix:
                    doc_id = prefix.split('quotation_document_id_')[1].split('__')[0]
                    record_info = f" (Linked to Quotation Document ID: {doc_id})"
            
            _logger.error("[ORPHAN RECORD] Broken PDF document detected and ignored%s. Error: %s", record_info, e)
            return

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """
        Override to catch and log orphan records during stream preparation.
        """
        try:
            return super(IrActionsReport, self)._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        except Exception as e:
            report = self._get_report(report_ref)
            _logger.error("[ORPHAN RECORD ERROR] Failed to prepare report streams for %s (IDs: %s). Error: %s", 
                         report.report_name, res_ids, e)
            raise
