import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
	ensure_hr_offer_customizations()


def after_migrate():
	ensure_hr_offer_customizations()


def ensure_hr_offer_customizations():
	_ensure_job_applicant_fields()
	_ensure_job_offer_fields()
	_ensure_job_applicant_layout()
	frappe.clear_cache(doctype="Job Applicant")
	frappe.clear_cache(doctype="Job Offer")
	frappe.db.commit()


def _ensure_job_applicant_fields():
	job_applicant_meta = frappe.get_meta("Job Applicant")
	address_anchor = _pick_last_existing_field(
		job_applicant_meta,
		["phone_number", "email_id", "applicant_name"],
	) or "phone_number"

	create_custom_fields(
		{
			"Job Applicant": [
				{
					"fieldname": "custom_full_address",
					"fieldtype": "Small Text",
					"label": "Full Address",
					"insert_after": address_anchor,
				},
			]
		},
		update=True,
	)


def _ensure_job_offer_fields():
	job_offer_meta = frappe.get_meta("Job Offer")
	primary_anchor = _pick_last_existing_field(
		job_offer_meta,
		["applicant_email_address", "applicant_email", "applicant_name", "job_applicant"],
	) or "job_applicant"

	create_custom_fields(
		{
			"Job Offer": [
				{
					"fieldname": "custom_applicant_phone_number",
					"fieldtype": "Data",
					"label": "Applicant Phone Number",
					"options": "Phone",
					"fetch_from": "job_applicant.phone_number",
					"read_only": 1,
					"insert_after": primary_anchor,
				},
				{
					"fieldname": "custom_applicant_full_address",
					"fieldtype": "Small Text",
					"label": "Applicant Address",
					"fetch_from": "job_applicant.custom_full_address",
					"read_only": 1,
					"insert_after": "custom_applicant_phone_number",
				},
			]
		},
		update=True,
	)


def _ensure_job_applicant_layout():
	_ensure_property_setter("Job Applicant", "country", "insert_after", "status", "Data")
	_ensure_property_setter("Job Applicant", "source_and_rating_section", "collapsible", "1", "Check")
	_ensure_property_setter("Job Applicant", "section_break_6", "collapsible", "1", "Check")
	_ensure_property_setter("Job Applicant", "section_break_6", "collapsed", "1", "Check")
	_ensure_property_setter("Job Applicant", "section_break_16", "collapsible", "1", "Check")
	_ensure_property_setter("Job Applicant", "section_break_16", "collapsed", "1", "Check")


def _ensure_property_setter(doc_type, field_name, property_name, value, property_type):
	filters = {
		"doc_type": doc_type,
		"field_name": field_name,
		"property": property_name,
		"doctype_or_field": "DocField",
	}
	name = frappe.db.get_value("Property Setter", filters, "name")
	if name:
		doc = frappe.get_doc("Property Setter", name)
		doc.value = str(value)
		doc.property_type = property_type
		doc.save(ignore_permissions=True)
		return

	frappe.get_doc(
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": doc_type,
			"field_name": field_name,
			"property": property_name,
			"value": str(value),
			"property_type": property_type,
		}
	).insert(ignore_permissions=True)


def _pick_last_existing_field(meta, fieldnames):
	field_order = {
		df.fieldname: idx
		for idx, df in enumerate(meta.fields or [])
		if getattr(df, "fieldname", None)
	}
	matches = [fieldname for fieldname in fieldnames if fieldname in field_order]
	if not matches:
		return None
	return max(matches, key=lambda fieldname: field_order[fieldname])
