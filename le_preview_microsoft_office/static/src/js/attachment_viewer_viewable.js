/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';

registerPatch({
	name: 'AttachmentViewerViewable',

	fields: {
		isOffice: attr({
			compute() {
				return this.attachmentOwner.isOffice;
			},
		}),
	},
});
