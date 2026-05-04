app_name = "snrg_hr"
app_title = "SNRG HR"
app_publisher = "SNRG Electricals"
app_description = "Custom ERPNext HR automation for SNRG Electricals"
app_email = "admin@snrgelectricals.com"
app_license = "MIT"

after_install = "snrg_hr.setup.after_install"
after_migrate = "snrg_hr.setup.after_migrate"

fixtures = []

doctype_js = {
	"Job Offer": "public/js/job_offer.js",
}

doc_events = {
	"Job Offer": {
		"autoname": "snrg_hr.api.job_offer.autoname",
		"before_insert": "snrg_hr.api.job_offer.before_insert",
		"validate": "snrg_hr.api.job_offer.validate",
		"after_insert": "snrg_hr.api.job_offer.sync_applicant_attachments",
		"on_update": "snrg_hr.api.job_offer.sync_applicant_attachments",
	},
}

# app_include_css = "/assets/snrg_hr/css/snrg_hr.css"
# app_include_js = "/assets/snrg_hr/js/snrg_hr.js"
