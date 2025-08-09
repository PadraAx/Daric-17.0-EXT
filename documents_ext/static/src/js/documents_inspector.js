/** @odoo-module **/

import {inspectorFields} from "@documents/views/inspector/documents_inspector";


 
inspectorFields.push("is_manager");

// inspectorFields.include({

//     updateAttachmentOriginal: function () {
        
//         const props = nextProps || this.props;
//         const record = props.documents[0];
//         if (props.documents.length !== 1) {
//             this.state.showChatter = this.isMobile;
//         }
//         if (!record || props.documents.length !== 1 || !record.data.orginal_attachment_ids.count) {
//             this.keepLast.add(Promise.resolve());
//             this.state.previousAttachmentData = null;
//             return;
//         }
//         const previousRecord = this.props.documents.length === 1 && this.props.documents[0];
//         if (
//             nextProps &&
//             previousRecord &&
//             previousRecord.resId === record.resId &&
//             !this.state.previousAttachmentDirty
//         ) {
//             return;
//         }
//         this.keepLast.add(
//             this.orm
//                 .searchRead(
//                     "ir.attachment",
//                     [
//                         [
//                             "id",
//                             "in",
//                             record.data.orginal_attachment_ids.records.map((rec) => rec.resId),
//                         ],
//                     ],
//                     ["name", "create_date", "create_uid"],
//                     {
//                         order: "create_date desc",
//                     }
//                 )
//                 .then((result) => {
//                     this.state.previousAttachmentData = result;
//                     this.state.previousAttachmentDirty = false;
//                 })
//         );
//     },
// });

   

