from odoo import http
from odoo.http import request


class KnowledgeRequest(http.Controller):
    @http.route('/knowledge/request/send', type='json', auth='user')
    def send_request(self, res_id, **kw):
        if res_id:
            knowledge = request.env['knowledge.article'].sudo().browse(res_id)
            if knowledge:
                if knowledge.category=='workspace':
                    return "ERROR: You can not share this article."
                has_request_ref = request.env['knowledge.request'].sudo().search([('requester','=',request.env.user.id),('article_id','=',knowledge.id)])
                if not has_request_ref :
                    item = request.env['knowledge.request'].sudo().create({
                        'requester': request.env.user.id,
                        'article_id': knowledge.id,
                        'content': knowledge.body,
                        'icon': knowledge.icon,
                        'cover_image_id': knowledge.cover_image_id.id,
                    })
                    return {
                        'message':"SUCCESS: The request was successfully registered.",
                        'id':item.id,
                        'showBtn':True
                    }
                else:
                    return {
                        'message':"INFO: Your request has been already registered.",
                        'id':has_request_ref.id,
                        'showBtn':True
                    }
        else:
            return {
                'message':"ERROR: An error occurred in the registration of the request.",
                'id':has_request_ref.id,
                'showBtn':False
            }
