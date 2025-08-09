/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { KanbanHeader } from '@web/views/kanban/kanban_header';
import { useService } from '@web/core/utils/hooks';
import { useState } from '@odoo/owl';

const RISKS_OF_EACH_COLUMN = 10;
patch(KanbanHeader.prototype, {
    setup() {
        super.setup();

        this.orm = useService('orm');
        this.action = useService('action');

        this.state = useState({
            modelName: '',
        });

        // Extract the model name
        this.getModuleName();

        if (this.state.modelName == 'erm.risk.template') {
            setTimeout(() => {

                // Get matrix colors
                this.setMatrixColors();

                // Get matrix likelihoods
                this.setMatrixLikelihoods();

                // Get matrix impacts
                this.setMatrixImpacts();

                // Set card numbers
                this.setCardNumbers();

                // Change 'Load more...' buttons onclick
                this.changeButtons();

                // Make cards undraggable
                this.makeCardsUndraggable();

                // Mark risk scores in matrix
                this.setRiskScores();

            }, 1000);
        }
    },

    getModuleName() {
        const inputString = window.location.href;
        const startIndex = inputString.indexOf('model=');
        if (startIndex !== -1) {
            const endIndex = inputString.indexOf('&', startIndex);
            this.state.modelName = endIndex !== -1
                ? inputString.substring(startIndex + 6, endIndex)
                : inputString.substring(startIndex + 6);
        }
    },

    async setMatrixColors() {
        try {
            let consequences = await this.orm.call(
                'erm.risk.template',
                'getConsequences',
                [['color', 'min', 'max']]
            );

            let matrixCells = document.querySelectorAll('.matrix-cell');
            consequences.forEach(consItem => {
                matrixCells.forEach(matItem => {
                    let riskScore = Number(matItem.getAttribute('risk-score-data'));
                    if (riskScore <= consItem.max && riskScore >= consItem.min) {
                        matItem.style.backgroundColor = consItem.color;
                    }
                });
            });

        } catch (error) {
            console.error('Error while getting colors:', error)
        }
    },

    async setMatrixLikelihoods() {
        try {
            let likelihoods = await this.orm.call(
                'erm.risk.template',
                'getLikelihoods',
                [['name', 'value']]
            );

            likelihoods.forEach(likeItem => {
                let name = likeItem.name.match(/[a-zA-Z]/g).join('');
                let value = likeItem.value;

                if (value == 1) {
                    let likelihoodNumber1 = $('.likelihood-number1');
                    for (let i = 0; i < likelihoodNumber1.length; i++) {
                        likelihoodNumber1[i].innerText = value
                    }

                    let likelihoodText1 = $('.likelihood-text1');
                    for (let i = 0; i < likelihoodText1.length; i++) {
                        likelihoodText1[i].innerText = name
                    }
                }

                else if (value == 2) {
                    let likelihoodNumber2 = $('.likelihood-number2');
                    for (let i = 0; i < likelihoodNumber2.length; i++) {
                        likelihoodNumber2[i].innerText = value
                    }

                    let likelihoodText2 = $('.likelihood-text2');
                    for (let i = 0; i < likelihoodText2.length; i++) {
                        likelihoodText2[i].innerText = name
                    }
                }

                else if (value == 3) {
                    let likelihoodNumber3 = $('.likelihood-number3');
                    for (let i = 0; i < likelihoodNumber3.length; i++) {
                        likelihoodNumber3[i].innerText = value
                    }

                    let likelihoodText3 = $('.likelihood-text3');
                    for (let i = 0; i < likelihoodText3.length; i++) {
                        likelihoodText3[i].innerText = name
                    }
                }

                else if (value == 4) {
                    let likelihoodNumber4 = $('.likelihood-number4');
                    for (let i = 0; i < likelihoodNumber4.length; i++) {
                        likelihoodNumber4[i].innerText = value
                    }

                    let likelihoodText4 = $('.likelihood-text4');
                    for (let i = 0; i < likelihoodText4.length; i++) {
                        likelihoodText4[i].innerText = name
                    }
                }

                else if (value == 5) {
                    let likelihoodNumber5 = $('.likelihood-number5');
                    for (let i = 0; i < likelihoodNumber5.length; i++) {
                        likelihoodNumber5[i].innerText = value
                    }

                    let likelihoodText5 = $('.likelihood-text5');
                    for (let i = 0; i < likelihoodText5.length; i++) {
                        likelihoodText5[i].innerText = name
                    }
                }

                else {
                    console.error('Invalid value for likelihood!');
                }
            });

        } catch (error) {
            console.error('Error while getting likelihoods:', error)
        }
    },

    async setMatrixImpacts() {
        try {
            let impacts = await this.orm.call(
                'erm.risk.template',
                'getImpacts',
                [['name', 'value']]
            );

            impacts.forEach(impItem => {
                let name = impItem.name.match(/[a-zA-Z]/g).join('');
                let value = impItem.value;

                if (value == 1) {
                    let impactNumber1 = $('.impact-number1');
                    for (let i = 0; i < impactNumber1.length; i++) {
                        impactNumber1[i].innerText = value
                    }

                    let impactText1 = $('.impact-text1');
                    for (let i = 0; i < impactText1.length; i++) {
                        impactText1[i].innerText = name
                    }
                }

                else if (value == 2) {
                    let impactNumber2 = $('.impact-number2');
                    for (let i = 0; i < impactNumber2.length; i++) {
                        impactNumber2[i].innerText = value
                    }

                    let impactText2 = $('.impact-text2');
                    for (let i = 0; i < impactText2.length; i++) {
                        impactText2[i].innerText = name
                    }
                }

                else if (value == 3) {
                    let impactNumber3 = $('.impact-number3');
                    for (let i = 0; i < impactNumber3.length; i++) {
                        impactNumber3[i].innerText = value
                    }

                    let impactText3 = $('.impact-text3');
                    for (let i = 0; i < impactText3.length; i++) {
                        impactText3[i].innerText = name
                    }
                }

                else if (value == 4) {
                    let impactNumber4 = $('.impact-number4');
                    for (let i = 0; i < impactNumber4.length; i++) {
                        impactNumber4[i].innerText = value
                    }

                    let impactText4 = $('.impact-text4');
                    for (let i = 0; i < impactText4.length; i++) {
                        impactText4[i].innerText = name
                    }
                }

                else if (value == 5) {
                    let impactNumber5 = $('.impact-number5');
                    for (let i = 0; i < impactNumber5.length; i++) {
                        impactNumber5[i].innerText = value
                    }

                    let impactText5 = $('.impact-text5');
                    for (let i = 0; i < impactText5.length; i++) {
                        impactText5[i].innerText = name
                    }
                }

                else {
                    console.error('Invalid value for likelihood!');
                }
            });

        } catch (error) {
            console.error('Error while getting impacts:', error)
        }
    },

    setCardNumbers() {
        let columns = document.querySelectorAll('.o_kanban_group');
        columns.forEach(column => {
            let cardNumbers = column.querySelectorAll('.risk-kanban-card-number');
            for (let i = 0; i < cardNumbers.length; i++) {
                cardNumbers[i].innerText = i + 1;
            }
        });
    },

    changeButtons() {
        let loadMoreButtons = document.querySelectorAll('.btn-outline-primary');
        for (let i = 0; i < loadMoreButtons.length; i++) {
            let button = loadMoreButtons[i];
            if (button.innerText.includes('Load more') && button.style.display != 'none') {
                button.style.display = 'none';

                let newButton = document.createElement('button');
                newButton.innerText = `See More... (${Number(button.innerText.match(/\d+/)[0])} remaining)`;
                newButton.classList.add('btn');
                newButton.classList.add('btn-outline-primary');
                newButton.classList.add('w-100');
                newButton.classList.add('mt-4');
                newButton.onclick = this.openRisksList.bind(this);
                button.parentElement.appendChild(newButton);
            }
        }
    },

    async openRisksList() {
        try {
            const actionData = await this.orm.call(
                'erm.risk.template',
                'openRisksList'
            );
            this.action.doAction(actionData);
        } catch (error) {
            console.error('Error while triggering action:', error);
        }
    },

    makeCardsUndraggable() {
        let cards = document.querySelectorAll('.o_draggable');
        cards.forEach(card => {
            card.classList.replace('o_draggable', 'o_undraggable');
        });
    },

    async setRiskScores() {
        try {
            let risks_group_by_category = await this.orm.call(
                'erm.risk.template',
                'getRisks',
                ['inherent_risk_score desc']
            );

            let columns = document.querySelectorAll('.o_column_title');

            risks_group_by_category.forEach(item => {
                let category_name = item.category_name;
                let risks = item.risks;

                if (risks.length > 0) {
                    columns.forEach(column => {
                        if (column.innerText == category_name) {
                            let matrixDiv = column.parentElement.parentElement.parentElement.querySelectorAll('.risk-matrix-div');
                            if (matrixDiv.length > 0) {
                                if (matrixDiv.length > 1) {
                                    console.error(`More than one matrix in a column: ${category_name}`);
                                }
                                else {
                                    let matrixCells = matrixDiv[0].querySelectorAll('.matrix-cell');
                                    for (let i = 0; i < risks.length && i < RISKS_OF_EACH_COLUMN; i++) {
                                        let cellPosition = (5 - risks[i].likelihood) * 5 + risks[i].impact - 1;
                                        if (matrixCells[cellPosition].innerHTML == '') {
                                            let newScore = document.createElement('div');
                                            newScore.innerText = i + 1;
                                            newScore.classList.add('score-in-matrix');
                                            newScore.onclick = this.openRiskForm.bind(this, risks[i].id);
                                            // or:
                                            // newScore.onclick = () => this.openRiskForm(risks[i].id);
                                            matrixCells[cellPosition].appendChild(newScore);
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            });

        } catch (error) {
            console.error('Error while getting risks:', error)
        }
    },

    async openRiskForm(risk_id) {
        try {
            const actionData = await this.orm.call(
                'erm.risk.template',
                'openRiskForm',
                [risk_id]
            );
            this.action.doAction(actionData);
        } catch (error) {
            console.error('Error while triggering action:', error);
        }
    },
});