odoo.define("sh_survey_extra_fields.survey", function (require) {
    "use strict";

    var core = require("web.core");
    var publicWidget = require("web.public.widget");
    require("survey.form");

    var field_utils = require('web.field_utils');
    var publicWidget = require('web.public.widget');
    var time = require('web.time');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var dom = require('web.dom');
    var utils = require('web.utils');

    var _t = core._t;


    publicWidget.registry.SurveyFormWidget.include({
        events: _.extend({}, publicWidget.registry.SurveyFormWidget.prototype.events || {}, {
            "change .js_cls_country_id": "_onChangeCountry",
            'change .sh_file_input': '_onChangeFileInput',
            "click .js_cls_sh_signature_clear_btn": "_onClickSignatureClearButton",
            "input input[type='range'].o_survey_question_email_box": "_onInputRangeValueChange",            
        }),

        /**
         * @override
         */
        init: function () {
            this.SH_FILE_DATA_DICTIONARY = {};
            this._super.apply(this, arguments);
        },
        
    	_onInputRangeValueChange: function (ev) {
			var $input = $(ev.currentTarget);
			$input.next('label').html($input.val())
		},
        
        /**
         * @private
         * @param {FileInputEvent} ev
         */
        _onChangeFileInput: async function (ev) {
            var self = this;
            
            var $fileUpload = $(ev.currentTarget);
            if ($fileUpload.length) {
                let FILE_LIST = new Array();
                const toBase64 = file => new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = error => reject(error);
                    reader.readAsDataURL(file);
                });
                async function ConvertBase64($fileUpload) {
                    for (let index = 0; index < $fileUpload[0].files.length; index++) {
                        const file = $fileUpload[0].files[index];
                        var file_data = await toBase64(file).then(function (result) {
                            var result_list = result.split(',');
                            if (result_list.length == 2) {
                                return result_list[1];
                            }
                        });
                        if (file_data) {
                            FILE_LIST.push({ 'fname': file.name, 'type': file.type, 'datas': file_data })
                        }
                    }
                }
                await ConvertBase64($fileUpload);
                self.SH_FILE_DATA_DICTIONARY[$fileUpload[0].name] = FILE_LIST;
            }
        },
        
        /**
         * Check if the URL is a valid or not.
         * @private
         */
        _validateURL: function (URL) {
        	
            var expression = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi;
            	        var regex = new RegExp(expression);
            	  
     
            	            if (URL.match(regex)) {
            	                return true;
            	            } else {
            	            	return false;
            	            }

         },     
        
        // VALIDATION TOOLS
        // -------------------------------------------------------------------------
        /**
        * Validation is done in frontend before submit to avoid latency from the server.
        * If the validation is incorrect, the errors are displayed before submitting and
        * fade in / out of submit is avoided.
        *
        * Each question type gets its own validation process.
        *
        * There is a special use case for the 'required' questions, where we use the constraint
        * error message that comes from the question configuration ('constr_error_msg' field).
        *
        * @private
        */
        _validateForm: function ($form, formData) {
            var self = this;
            var errors = {};
            var validationEmailMsg = _t("This answer must be an email address.");
            var validationDateMsg = _t("This is not a date");

            this._resetErrors();

            var data = {};
            formData.forEach(function (value, key) {
                data[key] = value;
            });

            var inactiveQuestionIds = this.options.sessionInProgress ? [] : this._getInactiveConditionalQuestionIds();

            $form.find('[data-question-type]').each(function () {
                var $input = $(this);
                var $questionWrapper = $input.closest(".js_question-wrapper");
                var questionId = $questionWrapper.attr('id');

                // If question is inactive, skip validation.
                if (inactiveQuestionIds.includes(parseInt(questionId))) {
                    return;
                }

                var questionRequired = $questionWrapper.data('required');
                var constrErrorMsg = $questionWrapper.data('constrErrorMsg');
                var validationErrorMsg = $questionWrapper.data('validationErrorMsg');
                switch ($input.data('questionType')) {
                    case 'char_box':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        } else if ($input.val() && $input.attr('type') === 'email' && !self._validateEmail($input.val())) {
                            errors[questionId] = validationEmailMsg;
                        } else {
                            var lengthMin = $input.data('validationLengthMin');
                            var lengthMax = $input.data('validationLengthMax');
                            var length = $input.val().length;
                            if (lengthMin && (lengthMin > length || length > lengthMax)) {
                                errors[questionId] = validationErrorMsg;
                            }
                        }
                        // softhealer pattern validation.
                        var pattern = $input.attr('pattern') || '';
                        if ($input.val() && pattern != '' ) {
                            // check pattern
                        	const re = new RegExp(pattern, 'g');
                        	const ok = re.test($input.val());
                        	if (!ok){
                            	errors[questionId] = constrErrorMsg;
                        	}
                        }
                        // softhealer pattern validation.
                        break;
                    case 'text_box':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;
                    case 'numerical_box':
                        if (questionRequired && !data[questionId]) {
                            errors[questionId] = constrErrorMsg;
                        } else {
                            var floatMin = $input.data('validationFloatMin');
                            var floatMax = $input.data('validationFloatMax');
                            var value = parseFloat($input.val());
                            if (floatMin && (floatMin > value || value > floatMax)) {
                                errors[questionId] = validationErrorMsg;
                            }
                        }
                        break;
                    case 'date':
                    case 'datetime':
                        if (questionRequired && !data[questionId]) {
                            errors[questionId] = constrErrorMsg;
                        } else if (data[questionId]) {
                            var datetimepickerFormat = $input.data('questionType') === 'datetime' ? time.getLangDatetimeFormat() : time.getLangDateFormat();
                            var momentDate = moment($input.val(), datetimepickerFormat);
                            if (!momentDate.isValid()) {
                                errors[questionId] = validationDateMsg;
                            } else {
                                var $dateDiv = $questionWrapper.find('.o_survey_form_date');
                                var maxDate = $dateDiv.data('maxdate');
                                var minDate = $dateDiv.data('mindate');
                                if ((maxDate && momentDate.isAfter(moment(maxDate)))
                                        || (minDate && momentDate.isBefore(moment(minDate)))) {
                                    errors[questionId] = validationErrorMsg;
                                }
                            }
                        }
                        break;
                    case 'simple_choice_radio':
                    case 'multiple_choice':
                        if (questionRequired) {
                            var $textarea = $questionWrapper.find('textarea');
                            if (!data[questionId]) {
                                errors[questionId] = constrErrorMsg;
                            } else if (data[questionId] === '-1' && !$textarea.val()) {
                                // if other has been checked and value is null
                                errors[questionId] = constrErrorMsg;
                            }
                        }
                        break;
                    case 'matrix':
                        if (questionRequired) {
                            var subQuestionsIds = $questionWrapper.find('table').data('subQuestions');
                            subQuestionsIds.forEach(function (id) {
                                if (!((questionId + '_' + id) in data)) {
                                    errors[questionId] = constrErrorMsg;
                                }
                            });
                        }
                        break;
                    case 'que_sh_email':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        if ($input.val() && !self._validateEmail($input.val())) {
                            errors[questionId] = validationEmailMsg;
                        }                        
                        break;
                    case 'que_sh_url':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        if ($input.val() && !self._validateURL($input.val())) {
                            errors[questionId] = _t("This answer must be an URL.");
                        }                        
                        break;

                    case 'que_sh_time':
                        var validationTimeErrorMsg = $input.parents('.js_question-wrapper').attr('data-validation-error-msg')
                        
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        if($input.val()){
                            var min = $input.attr('min')
                            var max = $input.attr('max')
                            var value = parseFloat($input.val())

                            if(parseFloat(min) > value || parseFloat(max) < value){
                                errors[questionId] = validationTimeErrorMsg || _('Time formate is not define properly.');
                            }

                        }
                        break;       

                    case 'que_sh_week':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;


                    case 'que_sh_month':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;
                    case 'que_sh_password':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;

                    case 'que_sh_file':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;

                    case 'que_sh_signature':
                        
                        var $pad = $input.closest(".js_cls_sh_signature_wrapper").find(".js_cls_sh_signature_pad");
                        var datapad = $pad.jSignature("getData", "native");
                        if (questionRequired && datapad.length == 0) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;
                    case 'que_sh_many2one':
                        if (questionRequired && !$input.val()) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;
                    case 'que_sh_many2many':
                        if (questionRequired && $input.find('.selected-items span').length == 0) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;
                    case 'que_sh_address':
                        if (questionRequired && !$input.val() && !$input.hasClass('js_cls_state_id')) {
                            errors[questionId] = constrErrorMsg;
                        }
                        break;
                }
            });
            if (_.keys(errors).length > 0) {
                this._showErrors(errors);
                return false;
            }
            return true;
        },
        
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * GET COUNTRIES
         * @private
         */
        getCountries: function () {
            var self = this;
            var $countrySelects = self.$target.find(".js_cls_country_id");
            if ($countrySelects.length) {
                self._rpc({
                    route: "/survey/get_countries",
                }).then(function (data) {
                    _.each(data.countries, function (x) {
                        var opt = $("<option>").text(x.name).attr("value", x.id);
                        $countrySelects.append(opt);
                    });
                });
            }
        },

        /**
         * GET Many2one Field Data
         * @private
         */
        getMany2oneFieldData: async function () {
            var self = this;
            var $m2oSelects = self.$target.find(".js_cls_sh_many2one_select");
            if ($m2oSelects.length) {
                await $m2oSelects.each(function (index, element) {
                    var model_id = $(this).attr("data-model_id") || false;
                    if (model_id) {
                        self._rpc({
                            route: "/survey/get_many2one_field_data",
                            params: {
                                model_id: parseInt(model_id),
                            },
                        }).then(function (data) {
                            _.each(data.records, function (x) {
                                var opt = $("<option>").text(x.name).attr("value", x.name);
                                $(element).append(opt);
                            });
                        });
                    }
                });
            }
        },

        /**
         * GET Many2many Field Data
         * @private
         */
        getMany2manyFieldData: function () {
            var self = this;
            var $m2oSelects = self.$target.find(".js_cls_sh_many2many_select");
            if ($m2oSelects.length) {
                $m2oSelects.each(function (index, element) {
                    var model_id = $(this).attr("data-model_id") || false;
                    if (model_id) {
                        self._rpc({
                            route: "/survey/get_many2many_field_data",
                            params: {
                                model_id: parseInt(model_id),
                            },
                        }).then(function (data) {
                            _.each(data.records, function (x) {
                                var opt = $("<option>").text(x.name).attr("value", x.name);
                                $(element).append(opt);
                            });

                            //init multi select
                            $(element).filterMultiSelect();
                        });
                    }
                });
            }
        },

        /**
         * GET Signature Field Data
         * @private
         */
        getSignatureFieldData: function () {
            var self = this;
            var $SignPad = self.$target.find(".js_cls_sh_signature_pad");
            if ($SignPad.length) {
                $SignPad.jSignature({
                    "background-color": "#808080",
                });

                //$SignPad.each(function( index, element ) {
                //});
            }
        },

        /**
         * Will automatically focus on the first input to allow the user to complete directly the survey,
         * without having to manually get the focus (only if the input has the right type - can write something inside -)
         */
        _focusOnFirstInput: function () {
            this._super.apply(this, arguments);

            if (this.$(".js_cls_country_id").length) {
                this.getCountries();
            }

            if (this.$(".js_cls_sh_many2one_select").length) {
                this.getMany2oneFieldData();
            }

            if (this.$(".js_cls_sh_many2many_select").length) {
                this.getMany2manyFieldData();
            }

            if (this.$(".js_cls_sh_signature_wrapper").length) {
                this.getSignatureFieldData();
            }
        },

        _onClickSignatureClearButton: function (ev) {
            var $clearButton = $(ev.currentTarget);
            var self = this;
            var $signpad = $clearButton.closest(".js_cls_sh_signature_wrapper").find(".js_cls_sh_signature_pad");
            $signpad.jSignature("reset");
        },

        /**
         *   _onChangeCountry .
         */

        _onChangeCountry: function (ev) {
            var $countrySelect = $(ev.currentTarget);
            var self = this;
            if (!$(ev.currentTarget).val()) {
                return;
            }

            this._rpc({
                route: "/survey/get_ountry_info/" + $(ev.currentTarget).val(),
            }).then(function (data) {
                // populate states and display
                var $stateSelect = $countrySelect.closest(".js_cls_sh_address_wrapper").find(".js_cls_state_id");
                // dont reload state at first loading (done in qweb)
                if ($stateSelect.length) {
                    if ($stateSelect.data("init") === 0 || $stateSelect.find("option").length === 1) {
                        if (data.states.length || data.state_required) {
                            $stateSelect.html("");
                            _.each(data.states, function (x) {
                                var opt = $("<option>").text(x[1]).attr("value", x[0]).attr("data-code", x[2]);
                                $stateSelect.append(opt);
                            });
                            $stateSelect.parent("div").show();
                        } else {
                            $stateSelect.val("").parent("div").hide();
                        }
                        $stateSelect.data("init", 0);
                    } else {
                        $stateSelect.data("init", 0);
                    }
                }
            });
        },

        /**
         *   Prepare Address answers before submitting form.
         */
        _prepareSubmitAnswersAddress: function (params, questionId, $address_ele) {
            var self = this;
            var $addressWrapper = $address_ele.closest(".js_cls_sh_address_wrapper");
            var street = $addressWrapper.find(".js_cls_street").val() || "";
            var street2 = $addressWrapper.find(".js_cls_street2").val() || "";
            var city = $addressWrapper.find(".js_cls_city").val() || "";
            var zip = $addressWrapper.find(".js_cls_zip").val() || "";
            var country_id = $addressWrapper.find(".js_cls_country_id").val() || "";
            var state_id = $addressWrapper.find(".js_cls_state_id").val() || "";

            if (street || street2 || city || zip || country_id || state_id) {
                var complete_address = "&street=" + street + "&street2=" + street2 + "&city=" + city + "&zip=" + zip + "&country_id=" + country_id + "&state_id=" + state_id;
                params[questionId] = complete_address;
            }
            return params;
        },

        /**
         *   Prepare Many2many answers before submitting form.
         */
        _prepareSubmitAnswersMany2many: function (params, $many2many_select_ele, questionId) {
            var self = this;
            $many2many_select_ele.find("input:checked").each(function () {
                if ($(this).val() != "") {
                    params = self._prepareSubmitAnswer(params, questionId, $(this).val());
                }
            });
            params = self._prepareSubmitComment(params, $many2many_select_ele, questionId, false);
            return params;
        },

        /**
         *   Prepare Signature answers before submitting form.
         */
        _prepareSubmitAnswersSignature: function (params, questionId, $signature_input_ele) {
            var self = this;
            var pad = $signature_input_ele.closest(".js_cls_sh_signature_wrapper").find(".js_cls_sh_signature_pad");
            var datapair = pad.jSignature("getData", "image");
            params[questionId] = datapair[1];
            return params;
        },

        _prepareSubmitValues: function (formData, params) {
            var self = this;
            formData.forEach(function (value, key) {
                switch (key) {
                    case "csrf_token":
                    case "token":
                    case "page_id":
                    case "question_id":
                        params[key] = value;
                        break;
                }
            });

            // Get all question answers by question type
            this.$("[data-question-type]").each(function () {
                switch ($(this).data("questionType")) {
                    case "text_box":
                    case "char_box":
                    case "numerical_box":
                        params[this.name] = this.value;
                        break;
                    case "date":
                        params = self._prepareSubmitDates(params, this.name, this.value, false);
                        break;
                    case "datetime":
                        params = self._prepareSubmitDates(params, this.name, this.value, true);
                        break;
                    case "simple_choice_radio":
                    case "multiple_choice":
                        params = self._prepareSubmitChoices(params, $(this), $(this).data("name"));
                        break;
                    case "matrix":
                        params = self._prepareSubmitAnswersMatrix(params, $(this));
                        break;
                    case "que_sh_color":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_email":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_url":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_time":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_range":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_week":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_month":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_password":
                        params[this.name] = this.value;
                        break;
                    case "que_sh_file":
                        params[this.name] = self.SH_FILE_DATA_DICTIONARY[this.name] || []
                        break;
                    case "que_sh_address":
                        params = self._prepareSubmitAnswersAddress(params, this.name, $(this));
                        break;
                    case "que_sh_many2one":
                        params[this.name] = $(this).parent().find("input").val();
                        break;
                    case "que_sh_many2many":
                        params = self._prepareSubmitAnswersMany2many(params, $(this), $(this).attr("name"));
                        break;
                    case "que_sh_signature":
                        params = self._prepareSubmitAnswersSignature(params, this.name, $(this));
                        break;
                }
            });
        },
    });
});

