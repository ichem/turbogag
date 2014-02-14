TurboGag Tutorial
=================

Letting users upload submissions
--------------------------------
Now we are going to let users upload submissions and we are going to enjoy some reddit re-posts. TurboGears controllers are Python classes inheriting from a special class called BaseController. Giving it a meaningful name is important. For example, the Root Controller is the controller class responding to your requested url path starting with "/" right after your domain. For example http://turbogag.com/submissions automatically maps to a child controller class or a class method called submissions.

We are going to create a submissions controller but first let's decide what actions we are going to have in it. 

* Our users will be able to post submissions. (create)
* A user will be able to update his submission. (update)
* A manager/moderator of TurboGag will be able to approve, update or delete user submissions. (moderate)
* Users will be able to comment on submissions.


.. code:: python

        # -*- coding: utf-8 -*-
    """Submissions controller module"""

    from tg import expose, redirect, validate, flash
    from tg import predicates

    from turbogag.lib.base import BaseController
    from turbogag.model import DBSession, metadata
    from turbogag.model.submission import Channel, Submission, Vote, Comment

    class SubmissionsController(BaseController):

        @expose("turbogag.templates.submissions.new")
        def new(self):
            channels = DBSession.query(Channel).all()
            return dict(channels=channels)

        @expose()
        def create(self, title, content_type, image_url="", video_url=""):
            submission = Submission(title=title, content_type=content_type, image_url=image_url, video_url=video_url, is_active=False)
            DBSession.add(submission)
            DBSession.flush()
            flash("Your submission has been received. It will be approved in a short notice.")
            return redirect("/")

        @expose("turbogag.templates.submissions.edit")
        def edit(self, submission_id):
            pass

        @expose()
        def update(self, id, title, content, status):
            pass

        @expose()
        def delete(self, id):
            pass

In the code above, we created class methods named "new", "create", "edit", "update" and "destroy". This class methods will be available to the users in the form of http://turbogag.com/submissions/{method_name}. For now there are only two actions available for our users to play with. 

1. In the ``new`` method we get a list of channels from the database and pass the channels list as a ``local template variable`` to our new.jinja template.
2. In the ``create`` method, we let our users send request parameters ``title``, ``content_type``, ``image_url`` and ``video_url``.
3. We are creating an instance of our ``Submission model`` and saving it to the database.
4. We are redirecting the user to our index page with a notification we will be displaying.



Embedding new controllers
-------------------------
If you tried accessing one of these pages via the browser, you will get a 404 error. In order to access those controllers, you have to introduce them to the RootController. Open your ``turbogag/controllers/root.py`` file and add the following line as an attribute.

.. code:: python

    # import the controller first
    from turbogag.controllers.submissions import SubmissionsController
    submissions = SubmissionsController()

Now if you re-visit http://127.0.0.1:8080/submissions/new you will be able to access this controller action. You will get an another error that we will fix in the next steps.


Something exposed comes this way
--------------------------------
If you have used Ruby on Rails, Django, Pylons or Pyramid there is a question in your head right from the start. I know that. Been there, done that. Where do I set my routes? TurboGears does not have a routing mechanism. You might think "Whoa sir, I'm afraid I cannot continue." No, not yet. TurboGears uses object dispatch which means every attribute in your RootController is a path of the url. Let's inspect the previous url: http://127.0.0.1:8080/submissions/new.

* You visit http://127.0.0.1:8080/submissions/new
* TurboGears looks at the RootController
* It looks for the submissions attribute in RootController
* If it does not find an attribute or a method named submissions, it returns 404.
* If it finds it, TurboGears calls that attribute
* It looks for another attribute "new" in SubmissionsController
* It returns it.

Basically you don't need to setup any routing for your application. Yes, that's right, that is totally cool. The expose decorator exposes that controller method to the web. If you don't decorate a method with "expose", it won't be accessible to the web and will just be a callable of your class.


Creating templates
------------------
Now that we have our controllers working for us, we can start building our forms and templates and fix all those errors. 


A taste of jQuery and Twitter Bootstrap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TurboGears 2.x comes with Twitter Bootstrap however for JavaScript goodness to work, we will include two libraries in our ``master.jinja`` template -which can be found at ``turbogag/templates`` directory-. Right before the ``</head>`` line in master.jinja file, add these two lines:

.. code:: html

    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
    <script type="text/javascript" src="{{ tg.url('/javascript/bootstrap.js') }}"></script>


Creating a new template
~~~~~~~~~~~~~~~~~~~~~~~
In the `turbogag/templates` folder, create a new directory called `submissions` and create two files. 

1) __init__.py so it becomes a package. 
2) new.jinja file.

.. code:: bash

    cd ~/projects/tg2-env/turbogag
    cd turbogag/templates
    mkdir submissions
    touch submissions/__init__.py
    touch Submissions/new.jinja

The following code snippet goes to ``templates/submissions/new.jinja`` file:

.. code:: jinja

    {% extends "master.jinja" %}

    {% block master_title %}Upload fun{% endblock %}

    {% block contents %}

        <ul class="nav nav-tabs" id="formTab">
            <li class="active"><a href="#pic" data-toggle="tab">Picture</a></li>
            <li><a href="#video" data-toggle="tab">Video</a></li>
        </ul>


        <div class="tab-content">
            <div id="pic" class="tab-pane active">
                <form class="form-horizontal" method="post" action="{{ url("/submissions/create") }}">
                    <input type="hidden" name="content_type" value="image" />
                    <div class="control-group">
                        <label class="control-label" for="title">Post Title:</label>
                        <div class="controls">
                            <input type="text" name="title" class="span5" />
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label" for="image_url">Image URL:</label>
                        <div class="controls">
                            <input type="text" name="image_url" class="span5" />
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label" for="channel">Channel:</label>
                        <div class="controls">
                            <div class="btn-group" data-toggle="buttons-radio">
                                {% for channel in channels %}
                                <button type="button" class="btn btn-primary">{{ channel.channel_name }}</button>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <button type="submit" class="btn btn-primary">Submit</button>
                        </div>
                    </div>
                </form>
            </div>
            <div id="video" class="tab-pane">
                <form class="form-horizontal" method="post" action="{{ url("/submissions/create") }}">
                    <input type="hidden" name="content_type" value="video" />
                    <div class="control-group">
                        <label class="control-label" for="title">Video Title:</label>
                        <div class="controls">
                            <input type="text" name="title" class="span5" />
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label" for="image_url">Video URL:</label>
                        <div class="controls">
                            <input type="text" name="video_url" class="span5" />
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label" for="channel">Channel:</label>
                        <div class="controls">
                            <div class="btn-group" data-toggle="buttons-radio">
                                {% for channel in channels %}
                                <button type="button" class="btn btn-primary">{{ channel.channel_name }}</button>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <button type="submit" class="btn btn-primary">Submit</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <script type="text/javascript">
        $(function(){
            $("#formTab").tab();
        });
        </script>

    {% endblock %}

Now visit http://127.0.0.1:8080/submissions/new and try creating a new submission. Your page will look like this:

.. image:: resources/new_submission.png
   :height: 500px

So far so good. Our users are able to post submissions but where do we list the submissions to visitors? Where do we approve the submissions? We are going to modify the ``index() method`` of ``RootController class`` and ``index.jinja`` template.

.. code:: python

    from turbogag.model import DBSession
    from turbogag.model.submission import Submission

    class RootController(BaseController):

        @expose('turbogag.templates.index')
        def index(self):
            """Handle the front-page."""
            submissions = DBSession.query(Submission).all()
            return dict(submissions=submissions)

And this is should be your ``turbogag/templates/index.jinja`` file:

.. code:: jinja

    {% extends "master.jinja" %}

    {% block master_title %}
    TurboGag.com
    {% endblock %}


    {% block contents %}
    <div class="row-fluid" >

        <div class="span10 content">
            {% for submission in submissions %}
            <div class="row-fluid submission">
                <div class="span8">
                    {% if submission.content_type == "image" %}
                    <img src="{{ submission.image_url }}" />
                    {% else %}
                    {% endif %}
                </div>
                <div class="span4">
                    <div class="submission-title"><a href="{{ url("/submissions/submission/%s" % submission.id) }}" />{{ submission.title }}</a></div>

                    <div class="poster"><a href="#">poster-info</a></div>

                    <div class="info">
                        <div class="row-fluid">
                            <div class="span1"><span class="comments">{{ submission.comments.count() }}</span></div>
                            <div class="span1" style="margin-left: 25px;"><span class="likes">{{ submission.votes.filter_by(liked=True).count() }}</span></div>
                        </div>
                    </div>

                    <div class="voting">
                        <div class="row-fluid">
                            <div class="votebox vb-first"><a href="{{ url("/submissions/vote/%s/good" % submission.id) }}" /><img src="{{ url("/images/sad.png") }}" /></a></div>
                            <div class="votebox vb-sec"><a href="{{ url("/submissions/vote/%s/bad" % submission.id) }}"><img src="{{ url("/images/happy.png") }}" /></a></div>
                        </div>
                    </div>

                    <div class="sharing">
                        <div class="row-fluid">
                            <div class="span6">
                                    <a href="https://twitter.com/share" class="twitter-share-button" data-url="{{ tg.url("/submissions/submission/%s" % submission.id) }}" data-via="turbogag" data-lang="en">Tweet</a>
                                    <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="https://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
                            </div>
                            <div class="span6">
                                <div class="fb-like" data-href="{{ tg.url("/submissions/submission/%s" % submission.id) }}" data-send="false" data-layout="button_count" data-width="125" data-show-faces="false"></div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
            <hr style="color: gray;" />
            {% endfor %}
        </div>
        
        <div class="span2">
        </div>

    </div>

    <div class="notice"> Thank you for choosing TurboGears.</div>

    {% endblock %}


