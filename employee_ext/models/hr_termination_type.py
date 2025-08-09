# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class TerminationType(models.Model):
    _name = 'hr.termination.type'
    _description = 'Termination Type'


    name = fields.Char(required=True, translate=True)


class RelationshipType(models.Model):
    _name = 'hr.relationship.type'
    _description = 'Relationship Type'


    name = fields.Char(required=True, translate=True)
    
    
class DocumentType(models.Model):
    _name = 'hr.document.type'
    _description = 'Document Type'


    name = fields.Char(required=True, translate=True)
