from odoo import models,fields

class Partner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        result = []
        for contact in self:
            if contact.is_company:
                print(contact.name)
                result.append((contact.id,contact.name))
        return result
