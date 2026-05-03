import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import now


def after_install():
	ensure_hr_offer_customizations()


def after_migrate():
	ensure_hr_offer_customizations()


def ensure_hr_offer_customizations():
	_ensure_job_applicant_fields()
	_ensure_job_offer_fields()
	_ensure_job_applicant_layout()
	_ensure_offer_term_seed_data()
	frappe.clear_cache(doctype="Job Applicant")
	frappe.clear_cache(doctype="Job Offer")
	frappe.clear_cache(doctype="Offer Term")
	frappe.clear_cache(doctype="Job Offer Term Template")
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
				{
					"fieldname": "custom_details_column_3",
					"fieldtype": "Column Break",
					"insert_after": "status",
				},
				{
					"fieldname": "custom_profile_resume_section",
					"fieldtype": "Section Break",
					"label": "Profile and Resume",
					"insert_after": "country",
				},
				{
					"fieldname": "custom_profile_resume_column_2",
					"fieldtype": "Column Break",
					"insert_after": "employee_referral",
				},
				{
					"fieldname": "custom_profile_resume_column_3",
					"fieldtype": "Column Break",
					"insert_after": "notes",
				},
			]
		},
		update=True,
		ignore_validate=True,
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
		ignore_validate=True,
	)


def _ensure_job_applicant_layout():
	_ensure_property_setter("Job Applicant", "country", "insert_after", "custom_full_address", "Data")
	_ensure_property_setter("Job Applicant", "currency", "insert_after", "custom_details_column_3", "Data")
	_ensure_property_setter("Job Applicant", "lower_range", "insert_after", "currency", "Data")
	_ensure_property_setter("Job Applicant", "upper_range", "insert_after", "lower_range", "Data")
	_ensure_property_setter("Job Applicant", "source_and_rating_section", "hidden", "1", "Check")
	_ensure_property_setter("Job Applicant", "section_break_6", "hidden", "1", "Check")
	_ensure_property_setter("Job Applicant", "section_break_16", "hidden", "1", "Check")
	_ensure_property_setter("Job Applicant", "source", "insert_after", "custom_profile_resume_section", "Data")
	_ensure_property_setter("Job Applicant", "source_name", "insert_after", "source", "Data")
	_ensure_property_setter("Job Applicant", "employee_referral", "insert_after", "source_name", "Data")
	_ensure_property_setter("Job Applicant", "applicant_rating", "insert_after", "custom_profile_resume_column_2", "Data")
	_ensure_property_setter("Job Applicant", "notes", "insert_after", "applicant_rating", "Data")
	_ensure_property_setter("Job Applicant", "cover_letter", "insert_after", "custom_profile_resume_column_3", "Data")
	_ensure_property_setter("Job Applicant", "resume_attachment", "insert_after", "cover_letter", "Data")
	_ensure_property_setter("Job Applicant", "resume_link", "insert_after", "resume_attachment", "Data")


def _ensure_offer_term_seed_data():
	terms = ("Territory", "Key Responsibilities", "Headquarter")
	for offer_term in terms:
		_insert_if_missing(
			"Offer Term",
			offer_term,
			{
				"offer_term": offer_term,
			},
		)

	template_name = "Sales Executive - LOI Standard"
	if not frappe.db.exists("Job Offer Term Template", template_name):
		_insert_if_missing(
			"Job Offer Term Template",
			template_name,
			{
				"title": template_name,
			},
		)

		seed_rows = [
			(
				"Territory",
				"State of Uttar Pradesh including Fatehpur District and Bundelkhand regions like Banda, Chitrakoot, Jhansi, Jalaun, Orai, Lalitpur and surrounding areas. The exact territory boundaries may be fine-tuned by the Company based on market potential and business requirements.",
			),
			(
				"Key Responsibilities",
				"Driving primary sales for the assigned geography\nAppointing and activating distributors and dealers\nEnsuring secondary sales movement and counter expansion\nMarket development, beat planning, and field execution\nAchieving monthly and quarterly sales targets\nSupporting collections and credit discipline\nEnsuring timely reporting and CRM compliance",
			),
			("Headquarter", "Fatehpur"),
		]

		for idx, (offer_term, value) in enumerate(seed_rows, start=1):
			child_name = f"{template_name}-{idx}"
			if frappe.db.exists("Job Offer Term", child_name):
				continue
			_insert_child_row(
				"Job Offer Term",
				child_name,
				template_name,
				"offer_terms",
				"Job Offer Term Template",
				idx,
				{
					"offer_term": offer_term,
					"value": value,
				},
			)


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


def _insert_if_missing(doctype, name, fields):
	if frappe.db.exists(doctype, name):
		return

	timestamp = now()
	columns = ["name", "creation", "modified", "modified_by", "owner", "docstatus"]
	values = [name, timestamp, timestamp, "Administrator", "Administrator", 0]

	for key, value in fields.items():
		columns.append(key)
		values.append(value)

	placeholders = ", ".join(["%s"] * len(columns))
	column_sql = ", ".join(f"`{column}`" for column in columns)
	frappe.db.sql(
		f"INSERT INTO `tab{doctype}` ({column_sql}) VALUES ({placeholders})",
		values,
	)


def _insert_child_row(doctype, name, parent, parentfield, parenttype, idx, fields):
	timestamp = now()
	columns = [
		"name",
		"creation",
		"modified",
		"modified_by",
		"owner",
		"docstatus",
		"parent",
		"parentfield",
		"parenttype",
		"idx",
	]
	values = [
		name,
		timestamp,
		timestamp,
		"Administrator",
		"Administrator",
		0,
		parent,
		parentfield,
		parenttype,
		idx,
	]

	for key, value in fields.items():
		columns.append(key)
		values.append(value)

	placeholders = ", ".join(["%s"] * len(columns))
	column_sql = ", ".join(f"`{column}`" for column in columns)
	frappe.db.sql(
		f"INSERT INTO `tab{doctype}` ({column_sql}) VALUES ({placeholders})",
		values,
	)
