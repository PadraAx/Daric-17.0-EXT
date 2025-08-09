# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import re
import requests

from markupsafe import Markup
from werkzeug.urls import url_encode

from odoo import _
from odoo.tools import image_process

from odoo.addons.web_editor import tools

# To detect if we have a valid URL or not
valid_url_regex = r'^(http://|https://|//)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(/.*)?$'

# Regex for few of the widely used video hosting services
player_regexes = {
    'youtube': r'^(?:(?:https?:)?//)?(?:www\.)?(?:youtu\.be/|youtube(-nocookie)?\.com/(?:embed/|v/|watch\?v=|watch\?.+&v=))((?:\w|-){11})\S*$',
    'vimeo': r'//(player.)?vimeo.com/([a-z]*/)*([0-9]{6,11})[?]?.*',
    'dailymotion': r'(https?:\/\/)(www\.)?(dailymotion\.com\/(embed\/video\/|embed\/|video\/|hub\/.*#video=)|dai\.ly\/)(?P<id>[A-Za-z0-9]{6,7})',
    'instagram': r'(?:(.*)instagram.com|instagr\.am)/p/(.[a-zA-Z0-9-_\.]*)',
    'youku': r'(?:(https?:\/\/)?(v\.youku\.com/v_show/id_|player\.youku\.com/player\.php/sid/|player\.youku\.com/embed/|cloud\.youku\.com/services/sharev\?vid=|video\.tudou\.com/v/)|youku:)(?P<id>[A-Za-z0-9]+)(?:\.html|/v\.swf|)',
}


def get_video_source_data(video_url):
    print('>>>>>>>>Call soure cdar>>>>>>>')
    """ Computes the valid source, document ID and regex match from given URL
        (or None in case of invalid URL).
    """
    if not video_url:
        return None

    if re.search(valid_url_regex, video_url):
       
            
        youtube_match = re.search(player_regexes['youtube'], video_url)
        if youtube_match:
            return ('youtube', youtube_match[2], youtube_match)
        vimeo_match = re.search(player_regexes['vimeo'], video_url)
        if vimeo_match:
            return ('vimeo', vimeo_match[3], vimeo_match)
        dailymotion_match = re.search(player_regexes['dailymotion'], video_url)
        if dailymotion_match:
            return ('dailymotion', dailymotion_match.group("id"), dailymotion_match)
        instagram_match = re.search(player_regexes['instagram'], video_url)
        if instagram_match:
            return ('instagram', instagram_match[2], instagram_match)
        youku_match = re.search(player_regexes['youku'], video_url)
        if youku_match:
            return ('youku', youku_match.group("id"), youku_match)
   
    count = 0
    if video_url.endswith('.mp4'):
        count += 1
        return ('local',count , video_url)
    return None

tools.get_video_source_data = get_video_source_data