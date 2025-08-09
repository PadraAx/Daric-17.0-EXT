/** @odoo-module **/

import { ControlPanel } from '@web/webclient/control_panel/control_panel';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';
import { useService } from '@web/core/utils/hooks';

patch(ControlPanel.prototype, 'business_requirement_analysis.ControlPanelButton', {
    setup() {
        this._super();
        this.actionService = useService('action');
        this.relatedCount = 0;  // Initialize related_count
        this.currentRecordFields = {};  // Initialize object to store current record fields

        // Fetch both related count and current record fields in one call
        this._fetchRecordData();
    },

    getButtons() {
        const buttons = this._super();

        // Create the smart button with the related count
        const customButton = {
            name: `Related Records (${this.relatedCount})`,  // Display the count
            class: 'btn btn-primary o_cp_button fa-file-text-o',
            type: 'button',
            action: this._onCustomButtonClick.bind(this),
        };

        // Add the button to the control panel
        buttons.push(customButton);
        return buttons;
    },

    _fetchRecordData() {
        // Fetch the related count and current record fields from the server in one RPC call
        rpc({
            route: '/business_requirement_analysis/get_record_data',
            params: {
                model: 'requierment',  // Replace with your actual model name
                id: this.props.active_id  // Pass the active record ID to the backend
            },
        }).then((result) => {
            this.relatedCount = result.related_count;  // Update the related count
            this.currentRecordFields = result.fields;  // Store the current record's fields
            this.render();  // Re-render the control panel to show the updated count
        });
    },

    _onCustomButtonClick() {
        // Example: Using a field called 'partner_id' to dynamically build the domain
        const workspace_id = this.currentRecordFields.workspace_id || false;

        // Action when the button is clicked with a dynamic domain based on current record fields
        this.actionService.doAction({
            name: 'Documents',
            type: 'ir.actions.act_window',
            res_model: 'related.model',
            view_mode: 'tree,form',
            domain: [['folder_id', '=', workspace_id]],
            context: {'create': False},
        });
    },
});

