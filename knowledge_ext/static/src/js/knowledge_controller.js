/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillStart, useChildSubEnv, useRef } from "@odoo/owl";
import { KnowledgeArticleFormController } from '@knowledge/js/knowledge_controller';
import { ArticleTemplatePickerDialog } from "@knowledge/components/article_template_picker_dialog/article_template_picker_dialog";

patch(
    KnowledgeArticleFormController.prototype,
    {
        setup() {
            super.setup();
            useChildSubEnv({
                createArticle: this.createArticle.bind(this),
                createArticleSecond: this.createArticleSecond.bind(this),
                ensureArticleName: this.ensureArticleName.bind(this),
                openArticle: this.openArticle.bind(this),
                renameArticle: this.renameArticle.bind(this),
                toggleAsideMobile: this.toggleAsideMobile.bind(this),
                topbarMountedPromise: this.topbarMountedPromise,
            });
        },

        async createArticleSecond() {
            this.dialogService.add(ArticleTemplatePickerDialog, {
                onLoadTemplate: async articleTemplateId => {
                    const articleId = await this.orm.call("knowledge.article", "apply_new_template", [], {
                        template_id: articleTemplateId,
                    });
                    await this.actionService.doAction("knowledge.ir_actions_server_knowledge_home_page", {
                        stackPosition: "replaceCurrentAction",
                        additionalContext: {
                            res_id: articleId
                        }
                    });
                }
            });
    
            // this.openArticle(articleId);
        }
    }


  );

