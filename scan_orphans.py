# -*- coding: utf-8 -*-

def scan_orphans(env):
    print("--- STARTING ORPHAN RECORD SCAN ---")
    
    # 1. Broken Attachments
    attachments = env['ir.attachment'].search([('type', '=', 'binary')])
    broken_attachments = []
    for att in attachments:
        try:
            if not att.raw:
                broken_attachments.append(att)
        except Exception:
            broken_attachments.append(att)
    
    if broken_attachments:
        print(f"\nFOUND {len(broken_attachments)} BROKEN ATTACHMENTS:")
        for att in broken_attachments:
            print(f"  [ORPHAN ATTACHMENT] ID: {att.id}, Name: {att.name}, Model: {att.res_model}, Res ID: {att.res_id}")
    else:
        print("\nNo broken attachments found.")
        
    # 2. Sale Order Lines without Order
    orphan_sol = env['sale.order.line'].search([('order_id', '=', False)])
    if orphan_sol:
        print(f"\nFOUND {len(orphan_sol)} ORPHAN SALE ORDER LINES:")
        for line in orphan_sol:
            print(f"  [ORPHAN SOL] ID: {line.id}, Name: {line.name}")
    else:
        print("\nNo orphan Sale Order Lines found.")
        
    # 3. Purchase Order Lines without Order
    orphan_pol = env['purchase.order.line'].search([('order_id', '=', False)])
    if orphan_pol:
        print(f"\nFOUND {len(orphan_pol)} ORPHAN PURCHASE ORDER LINES:")
        for line in orphan_pol:
            print(f"  [ORPHAN POL] ID: {line.id}, Name: {line.name}")
    else:
        print("\nNo orphan Purchase Order Lines found.")
        
    # 4. Sale PDF Quote Builder Documents
    if 'quotation.document' in env:
        q_docs = env['quotation.document'].search([])
        broken_qdocs = q_docs.filtered(lambda d: not d.datas)
        if broken_qdocs:
            print(f"\nFOUND {len(broken_qdocs)} BROKEN QUOTATION DOCUMENTS:")
            for doc in broken_qdocs:
                print(f"  [ORPHAN QDOC] ID: {doc.id}, Name: {doc.name}")
                
    if 'product.document' in env:
        p_docs = env['product.document'].search([])
        broken_pdocs = p_docs.filtered(lambda d: not d.datas)
        if broken_pdocs:
            print(f"\nFOUND {len(broken_pdocs)} BROKEN PRODUCT DOCUMENTS:")
            for doc in broken_pdocs:
                print(f"  [ORPHAN PDOC] ID: {doc.id}, Name: {doc.name}")

    print("\n--- SCAN COMPLETE ---")

if __name__ == '__main__':
    scan_orphans(env)
