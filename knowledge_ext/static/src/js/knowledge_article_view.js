/** @odoo-module */

import { formView } from '@web/views/form/form_view';
import { registry } from "@web/core/registry";
import { KnowledgeArticleFormController } from './knowledge_article_controller.js';
import { KnowledgeArticleFormRenderer } from './knowledge_article_renderers.js';


export const knowledgeArticleFormView = {
    ...formView,
    Controller: KnowledgeArticleFormController,
    Renderer: KnowledgeArticleFormRenderer
};

registry.category('views').add('knowledge_article_extra_view_form', knowledgeArticleFormView);
