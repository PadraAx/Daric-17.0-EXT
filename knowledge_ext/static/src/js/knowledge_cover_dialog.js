/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { KnowledgeCoverSelector } from "@knowledge/components/knowledge_cover/knowledge_cover_dialog";

patch(
    KnowledgeCoverSelector.prototype,
    {
        async fetchAttachments(limit, offset) {
            this.state.isFetchingAttachments = true;
            let attachments = [];
            let recordDate = await this.orm.call('knowledge.article', 'get_user_attachment_ids', [])
            let domain = ['&','&', ['res_model', '=', this.props.resModel], ['name', 'ilike', this.state.needle], ['id', 'in', recordDate]]
            debugger;
            try {
                attachments = await this.orm.call(
                    'ir.attachment',
                    'search_read',
                    [],
                    {
                        domain: domain,
                        fields: ['name', 'mimetype', 'description', 'checksum', 'url', 'type', 'res_id', 'res_model', 'public', 'access_token', 'image_src', 'image_width', 'image_height', 'original_id'],
                        order: 'id desc',
                        limit,
                        offset,
                    }
                );
                attachments.forEach(attachment => attachment.mediaType = 'attachment');
            } catch (e) {
                if (e.exceptionName !== 'odoo.exceptions.AccessError') {
                    throw e;
                }
            }
            this.state.canLoadMoreAttachments = attachments.length >= this.NUMBER_OF_ATTACHMENTS_TO_DISPLAY;
            this.state.isFetchingAttachments = false;
            return attachments;
        }, 
    }
);