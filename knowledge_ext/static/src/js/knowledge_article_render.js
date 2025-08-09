/** @odoo-module **/

import { knowledgeTopbar } from '@knowledge/components/topbar/topbar';
import { KnowledgeHtmlAlertDialog } from "../html_confirm_dialog/html_confirm_dialog";


class KnowledgeTopbarExt extends knowledgeTopbar.component{
  async onSendRequestClick() {
        console.log('test')
        debugger;
        await this.props.record.save();
        this.dialog.add(KnowledgeHtmlAlertDialog, {
          body: "Are you sure you want to publish this article?",
          title: "Confirmation",
          confirm: async () => {
            const request = await this.rpc("/knowledge/request/send", {
              res_id: this.props.record.resId,
            });
            this.dialog.add(KnowledgeHtmlAlertDialog, {
              body: request.message,
              id: request.id,
              showButton: request.showBtn,
              ViewTaskLabel: "View Request ",
            });
          },
          cancel: () => {},
        });
      }
}
knowledgeTopbar.component = KnowledgeTopbarExt;




// patch(KnowledgeTopbar.prototype, {
//   // setup() {
//   //   this._super(...arguments);
//   // },

//   async onSendRequestClick() {
//     console.log('test')
//     // await this.props.record.save();
//     // this.dialog.add(KnowledgeHtmlAlertDialog, {
//     //   body: "Are you sure you want to publish this article?",
//     //   title: "Confirmation",
//     //   confirm: async () => {
//     //     const request = await this.rpc("/knowledge/request/send", {
//     //       res_id: this.resId,
//     //     });
//     //     this.dialog.add(KnowledgeHtmlAlertDialog, {
//     //       body: request.message,
//     //       id: request.id,
//     //       showButton: request.showBtn,
//     //       ViewTaskLabel: "View Request ",
//     //     });
//     //   },
//     //   cancel: () => {},
//     // });
//   },

//   // async createArticle(category, targetParentId) {
//   //   this.actionService.doAction({
//   //     name: "Select Template",
//   //     res_model: "wizard.template",
//   //     type: "ir.actions.act_window",
//   //     views: [[false, "form"]],
//   //     view_mode: "form",
//   //     context: {
//   //       default_is_private: category,
//   //       default_article_id: targetParentId,
//   //     },
//   //     target: "new",
//   //   });
//   // },
//   // _showEmojiPicker(ev) {
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super(ev);
//   // },
//   // addIcon() {
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super();
//   // },
//   // addCover(event) {
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super(event);
//   // },
//   // onChangeCoverClick() {
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super();
//   // },
//   // openCoverSelector() {
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super();
//   // },
//   // addProperties(event){
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super(event);
//   // },
//   // toggleProperties(){
//   //   var access = this.props.record.data.access_content;
//   //   if(access != undefined && access==false){
//   //     return
//   //   }
//   //   this._super();
//   // }
// });


