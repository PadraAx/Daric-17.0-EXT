/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { VideoSelector } from '@web_editor/components/media_dialog/video_selector';
console.log('>>>>>>>>>.call video sleecrt>>>>>>')
patch(VideoSelector.prototype, {
    setup() {
        super.setup(...arguments);
        var self = this;
          //    use uppy to handle upload video
          var uppy = Uppy.Core({
              debug: true,
              meta: {
                  csrf_token: odoo.csrf_token
              },
              autoProceed: true,
              locale: Uppy.locales.en_US,
              allowMultipleUploads: false,
              restrictions: {
                  maxNumberOfFiles: 1,
                  allowedFileTypes: ['video/*', '.mp4']
              },
          });
          uppy.use(Uppy.Dashboard, {
              trigger: '.upload-trigger',
              closeAfterFinish: true,
              inline: false,
              proudlyDisplayPoweredByUppy: false,
              showProgressDetails: true
          });
          uppy.use(Uppy.Webcam, {
              target: Uppy.Dashboard,
              title: '摄像头(https)'
          });
          uppy.use(Uppy.ScreenCapture, {
              target: Uppy.Dashboard,
              title: '屏幕录制'
          });
          uppy.use(Uppy.XHRUpload, {
              endpoint: location.origin + '/videos/upload/process',
              fieldName: 'file'
          });
          uppy.on('upload-success', (file, response) => {
              // HTTP status code
              // extracted response data
              console.log('*********upload-success************',response, file)
              const videoUrl = response.body.url;
            //   this.updateVideoViaUrl(videoUrl);
            this.state.urlInput = videoUrl;
            this.updateVideo();
          });
          this.uppy = uppy;
    },
    _onClick() {
    
      this.uppy.getPlugin('Dashboard').openModal();
      console.log('=====click===agter===call thissss')
    },    
});
console.log('=====click===last===call thissss')