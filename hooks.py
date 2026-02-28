from . import __version__ as app_version

app_name = "ampower_fleetman"
app_title = "AmPower FleetMan"
app_publisher = "Ambibuzz Technologies LLP"
app_description = "AmPower Fleet Maintenance and Management Solution"
app_email = "buzz@ampower.cloud"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ampower_fleetman/css/ampower_fleetman.css"
# app_include_js = "/assets/ampower_fleetman/js/ampower_fleetman.js"

# include js, css files in header of web template
# web_include_css = "/assets/ampower_fleetman/css/ampower_fleetman.css"
# web_include_js = "/assets/ampower_fleetman/js/ampower_fleetman.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ampower_fleetman/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "ampower_fleetman.utils.jinja_methods",
#	"filters": "ampower_fleetman.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ampower_fleetman.install.before_install"
# after_install = "ampower_fleetman.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ampower_fleetman.uninstall.before_uninstall"
# after_uninstall = "ampower_fleetman.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ampower_fleetman.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Trip": "ampower_fleetman.ampower_fleetman.override.trip.CustomTrip"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"ampower_fleetman.tasks.all"
	# ],
	"daily": [
		"ampower_fleetman.ampower_fleetman.task.vehicle_maintenance_alerts.main"
	],
	# "hourly": [
	# 	"ampower_fleetman.tasks.hourly"
	# ],
	# "weekly": [
	# 	"ampower_fleetman.tasks.weekly"
	# ],
	# "monthly": [
	# 	"ampower_fleetman.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "ampower_fleetman.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "ampower_fleetman.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "ampower_fleetman.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ampower_fleetman.utils.before_request"]
# after_request = ["ampower_fleetman.utils.after_request"]

# Job Events
# ----------
# before_job = ["ampower_fleetman.utils.before_job"]
# after_job = ["ampower_fleetman.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"ampower_fleetman.auth.validate"
# ]
fixtures = [
        {"dt": "Custom Field", "filters": [["module", "=", "AmPower FleetMan"]]},
        {"dt": "Property Setter", "filters": [["module", "=", "AmPower FleetMan"]]}
    ]

