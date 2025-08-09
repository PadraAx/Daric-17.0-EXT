/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { Attachment } from '@mail/core/common/attachment_model';
import { FileViewer } from '@web/core/file_viewer/file_viewer';
import { useService } from '@web/core/utils/hooks';

patch(Attachment.prototype, {
	get defaultSource() {
		var route = super.defaultSource;
		if (this.isOffice) {
			route = this.officeUrl;
		}
		return route;
	},
	get isViewable() {
		return (super.isViewable || this.isOffice) && !this.uploading;
	},
	get isOffice() {
		const officeMimeType = [
			'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'application/vnd.openxmlformats-officedocument.presentationml.presentation',
		];
		return officeMimeType.includes(this.mimetype);
	},

	set setOfficeUrl(url) {
		this.officeUrl = url;
	},
});

patch(FileViewer.prototype, {
	async setup() {
		super.setup();
		this.orm = useService('orm');

		var filteredFiles = this.props.files.filter((file) => file.isOffice);
		//? Tokens returns a list of tokens that *SHOULD* be in the same order as the submitted list
		var urls = await this.orm.call('ir.attachment', 'get_office_preview_link', [filteredFiles.map(({ id }) => id)]);

		filteredFiles.forEach((file, index) => {
			file.setOfficeUrl = urls[index];
		});
	},
});
