# -*- coding: utf-8 -*-
{
    'name': "Upload Local Video in Website Builder",

    'summary': """
        Allows users to upload local video using snippet in website builder""",

    'description': """
        Change the behavior of uploading video, when user build website, they can select video from their computer and upload to server
    """,
    'author': "TORAHOPER",
    'website': "https://torahoper.ir",
    'category': 'Website',
    'version': '1.0.1',
    'depends': ['base', 'website','web_editor'],
    'images': [
        'static/description/banner.png'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/snippets/s_video.xml',
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web_editor.assets_media_dialog': [
            'upload_video_snippet_pt/static/src/xml/*.xml',
            'upload_video_snippet_pt/static/src/js/video_selector.js',
        ],
         'website.assets_wysiwyg': [
            'upload_video_snippet_pt/static/lib/uppy/uppy.min.css',
            'upload_video_snippet_pt/static/lib/uppy/uppy.min.js',
            'upload_video_snippet_pt/static/lib/uppy/en_US.min.js',
            'upload_video_snippet_pt/static/src/css/snippets.css',
            'upload_video_snippet_pt/static/src/js/snippets/s_video/options.js',
        ],
    },
   'license': 'LGPL-3',
   "application":  True,
    'price': 64.99,
    'currency': 'USD',
}
