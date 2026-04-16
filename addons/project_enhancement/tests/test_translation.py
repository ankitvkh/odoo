import odoo.tests

@odoo.tests.tagged('post_install', '-at_install')
class TestProjectEnhancement(odoo.tests.TransactionCase):
    def test_translation_disabled(self):
        field = self.env['project.project']._fields['name']
        self.assertFalse(getattr(field, 'translate', False))
        print('\n\n--- TEST PASSED: translation is false ---\n\n')
