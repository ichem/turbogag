# -*- coding: utf-8 -*-
"""Main Controller"""
from sprox.tablebase import TableBase
from sprox.widgets import SproxDataGrid

from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from tgext.admin import CrudRestControllerConfig
from tgext.crud import CrudRestController
from turbogag import model
from turbogag.controllers.secure import SecureController
from turbogag.model import DBSession, metadata
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController

from turbogag.lib.base import BaseController
from turbogag.controllers.error import ErrorController
from turbogag.controllers.submissions import SubmissionsController
from turbogag.model import DBSession
from turbogag.model.submission import Submission

__all__ = ['RootController']

class TurboGagGrid(SproxDataGrid):
    css_class = "table table-striped table-bordered"


class SubmissionCrudRestController(CrudRestController):

    @expose("turbogag.templates.admin.get_all", inherit=True)
    #@paginate('value_list', items_per_page=7)
    def get_all(self, *args, **kwargs):
        return super(SubmissionCrudRestController, self).get_all(*args, **kwargs)

class MyAdminConfig(TGAdminConfig):

    class submission(CrudRestControllerConfig):
        defaultCrudRestController = SubmissionCrudRestController
        class table_type(TableBase):
            __base_widget_type__ = TurboGagGrid
            __entity__ = Submission
            __xml_fields__ = ["channel"]

            def channel(self, obj):
                return obj.channel.channel_name




class RootController(BaseController):
    """
    The root controller for the turbogag application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=MyAdminConfig)

    error = ErrorController()
    submissions = SubmissionsController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "turbogag"

    @expose('turbogag.templates.index')
    def index(self):
        """Handle the front-page."""
        submissions = DBSession.query(Submission).all()
        return dict(submissions=submissions)

    @expose('turbogag.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('turbogag.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('turbogag.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(page='data', params=kw)
    @expose('turbogag.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('turbogag.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('turbogag.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
