-- PSQL script to reset Odoo sequences for custom Sale and Purchase Orders to 1460

-- Reset Purchase Order Custom Sequence
UPDATE ir_sequence 
SET number_next = 1460 
WHERE code = 'purchase.order.custom';

-- Reset Sale Order Custom Sequence
UPDATE ir_sequence 
SET number_next = 1460 
WHERE code = 'sale.order.custom';

-- If use_advisory_lock is true, we might need to reset the actual postgres sequence too
-- However, Odoo's next_by_code usually manages this via the ir_sequence table if implementation is 'standard'

-- To see the effect, you can run:
-- SELECT name, code, number_next FROM ir_sequence WHERE code IN ('purchase.order.custom', 'sale.order.custom');
