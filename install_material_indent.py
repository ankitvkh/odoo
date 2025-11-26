# Install material_indent module
try:
    material_indent = env['ir.module.module'].search([('name', '=', 'material_indent')])
    if material_indent and material_indent.state == 'uninstalled':
        material_indent.button_immediate_install()
        print("Material Indent module installed successfully!")
    else:
        print(f"Module state: {material_indent.state if material_indent else 'Not found'}")
except Exception as e:
    print(f"Installation error: {e}")

env.cr.commit()