# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from flask import session

from indico.core import signals
from indico.core.logger import Logger
from indico.modules.events.features.base import EventFeature
from indico.util.i18n import _
from indico.web.flask.util import url_for
from MaKaC.webinterface.displayMgr import EventMenuEntry


logger = Logger.get('events.survey')


@signals.users.merged.connect
def _merge_users(target, source, **kwargs):
    from indico.modules.events.surveys.models.submissions import SurveySubmission
    SurveySubmission.find(user_id=source.id).update({SurveySubmission.user_id: target.id})


@signals.event_management.sidemenu.connect
def _extend_event_management_menu(event, **kwargs):
    from MaKaC.webinterface.wcomponents import SideMenuItem
    return 'surveys', SideMenuItem(_('Surveys'), url_for('survey.management', event),
                                   visible=event.canModify(session.user), event_feature='surveys')


@signals.event.sidemenu.connect
def _extend_event_menu(sender, **kwargs):
    from indico.modules.events.surveys.models.surveys import Survey

    def _visible(event):
        return bool(Survey.find(Survey.is_visible, Survey.event_id == int(event.id)).count())

    return EventMenuEntry('survey.display_survey_list', _('Surveys'), name='surveys', visible=_visible)


@signals.event.get_feature_definitions.connect
def _get_feature_definitions(sender, **kwargs):
    return SurveysFeature


class SurveysFeature(EventFeature):
    name = 'surveys'
    friendly_name = _('Surveys')
    description = _('Gives event managers the opportunity to create surveys.')

    @classmethod
    def is_default_for_event(cls, event):
        return True
