# Notifications plugin for FIR

## Features

This plugins allows you to send notifications to users.

## Installation

In your FIR virtualenv, launch:

```bash
(fir-env)$ pip install -r fir_notifications/requirements.txt
```

In *$FIR_HOME/fir/config/installed_app.txt*, add:

```
fir_notifications
```

In your *$FIR_HOME*, launch:

```bash
(fir-env)$ ./manage.py migrate fir_notifications
```

You should configure fir_celery (broker and result backend).

## Usage

Users can subscribe to notifications via their profile page.

Core FIR notifications:
* 'observation:created': new observation
* 'observation:updated': update of an observation
* 'finding:created': new finding
* 'finding:updated': update of an finding
* 'observation:commented': new comment added to an observation
* 'finding:commented': new comment added to an finding
* 'observation:status_changed': observation status changed
* 'finding:status_changed': finding status changed

## Configuration

### Observations

You can disable notification observations in the settings using the key `NOTIFICATIONS_DISABLED_EVENTS`:

```python
NOTIFICATIONS_DISABLED_EVENTS = ('observation:created', 'finding:created')
```

If you don't want to send different notification observations for Findings and Observations, you  should enable this setting:

```python
# Send 'finding:*' notification observations for both Observation and Finding if True
NOTIFICATIONS_MERGE_INCIDENTS_AND_EVENTS = True
```

### Celery

`fir_notifications` uses the FIR plugin `fir_celery`.

### Full URL in notification links

To generate correct URL in notification, `fir_notifications` needs to know the external URL of the FIR site:

``` python
EXTERNAL_URL = 'https://fir.example.com'
```

### Email notifications

Follow the `fir_email` [README](../fir_email/README.md).

### Jabber (XMPP) notifications

Configure `fir_notifications`:

``` python
# FIR user JID 
NOTIFICATIONS_XMPP_JID = 'fir@example.com'
# Password for fir@example.com JID
NOTIFICATIONS_XMPP_PASSWORD = 'my secret password'
# XMPP server
NOTIFICATIONS_XMPP_SERVER = 'localhost'
# XMPP server port
NOTIFICATIONS_XMPP_PORT = 5222
```

### Notification templates

You have to create at least onenotification template per notification observation in the Django admin site.

To render notifications, each notification method can use the fields `subject`, `description` or `short_description`:

- Email uses `subject` and `description`.
- XMPP uses `subject` and `short_description`.

These fields will accept Markdown formatted text and Django template language markups. The Django template context will contain an `instance`object, the instance of the object that fired the notification observation.

The Email `description` will generate a multipart message: a plain text part in Markdown and a HTML part rendered from this Markdown. The XMPP `short_description` will be rendered as HTML from Markdown.

The template used to send the notification to the user will be chosen from the templates available to this user:
- For a user with global permissions (permission from a Django group), global templates (templates with no nusiness line attached to it) will be preferred. 
- For a user with no global permission, the nearest business line template will be preferred, global templates will be used as a fallback.
## Hacking

### Adding notification method

You have to create a subclass of `NotificationMethod` from `fir_notifications.methods` and implement at least the `send` method. You can then register your method with `fir_notification.registry.registry.register_method`.

If your configuration method needs some additional user defined settings, you have to list them in the class property `options`. See `EmailMethod` and `XmppMethod` for details. 

### Adding notification observation

Use the `@notification_observation` decorator defined in `fir_notifications.decorators` to decorate a classic Django signal handler function. This handler must return a tuple with an instance of the notification model and a queryset of the concerned business lines.



