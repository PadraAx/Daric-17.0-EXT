/** @odoo-module **/
console.log('========call jssssss videosss-')
// import {weWidgets} from '@web_editor/js/wysiwyg/wysiwyg';
import { MediaDialog } from "@web_editor/components/media_dialog/media_dialog";
import options from '@web_editor/js/editor/snippets.options';

options.registry.hlcloudVideo = options.Class.extend({
    events: Object.assign({}, options.Class.prototype.events || {}, {
        'click we-button.add_video': '_onAddVideo',
    }),

    start: function () {
        var self = this;
        console.log('=========32534664')
        this.$target.on('dblclick', 'video', function (e) {
            self._onAddVideo(true);
        });
        return this._super.apply(this, arguments);
    },

    _onAddVideo: function (previewMode) {
        console.log('===call videoss=======23455344545')
        var self = this;
        var media = this.$target.find('video')[0];
        var videoSrc = media.dataset.oeExpression;
        if (videoSrc && videoSrc.startsWith('/')) {
            media.dataset.oeExpression = location.origin + videoSrc;
        }
        console.log('===call befoee call attch dialog=======23455344545')

        return new Promise(resolve => {
            let savedPromise = Promise.resolve();
            const props = {
                noImages: true, noDocuments: true, noIcons: true, media,
                save: media => {
                    var src = media.dataset.oeExpression;
                    if (src && src.endsWith('mp4')) {
                        //local
                        var $video =
                            '<video id="temp_video" style="width:100%;" loop="true" muted="true" autoplay="autoplay" controls="controls" data-oe-expression="' + src + '">\n' +
                            '   <source id="temp_video_source" src="' + src + '" type="video/mp4"/>\n' +
                            '   Your browser does not support the video tag.\n' +
                            '</video>';
                    } else {
                        // irframe
                        var $video =
                            '<div class="media_iframe_video" data-oe-expression="' + src + '">' +
                            '<div class="css_editable_mode_display">&nbsp;</div>' +
                            '<div class="media_iframe_video_size" contenteditable="false">&nbsp;</div>' +
                            '<iframe src="' + src + '" frameborder="0" contenteditable="false" allowfullscreen="allowfullscreen"></iframe>' +
                            '</div>';
                    }
    
                    self.$target.find('.container').html($video);
                },
            }
            console.log('======porps>>>',props)
            this.call("dialog", "add", MediaDialog, props, {
                onClose: () => {
                    savedPromise.then(resolve);
                },
            });
        });
    }
})
console.log('=====454==ca')

