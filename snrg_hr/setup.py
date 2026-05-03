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
	_ensure_job_offer_defaults()
	_ensure_offer_term_seed_data()
	_ensure_job_offer_print_format()
	frappe.clear_cache(doctype="Job Applicant")
	frappe.clear_cache(doctype="Job Offer")
	frappe.clear_cache(doctype="Offer Term")
	frappe.clear_cache(doctype="Job Offer Term Template")
	frappe.clear_cache(doctype="Print Format")
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
					"insert_after": "upper_range",
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


def _ensure_job_offer_defaults():
	_ensure_property_setter("Job Offer", "offer_date", "default", "Today", "Data")
	_ensure_property_setter("Job Offer", "letter_head", "default", "SNRG Blue Letter Head", "Data")


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


def _ensure_job_offer_print_format():
	name = "SNRG LOI Job Offer"
	html = """
{% set ns = namespace(territory='', responsibilities='', headquarter='') %}
{% for row in doc.offer_terms or [] %}
  {% if row.offer_term == "Territory" %}{% set ns.territory = row.value %}{% endif %}
  {% if row.offer_term == "Key Responsibilities" %}{% set ns.responsibilities = row.value %}{% endif %}
  {% if row.offer_term == "Headquarter" %}{% set ns.headquarter = row.value %}{% endif %}
{% endfor %}
{% set letter_head_content = letter_head.content if letter_head is mapping else letter_head %}

<style>
  .loi-wrap { font-family: Arial, sans-serif; font-size: 12px; line-height: 1.6; color: #222; }
  .loi-wrap h1 { font-size: 18px; margin: 0 0 16px; text-align: center; }
  .loi-wrap h2 { font-size: 14px; margin: 18px 0 8px; }
  .loi-wrap p { margin: 0 0 10px; }
  .loi-wrap ul { margin: 0 0 10px 18px; padding: 0; }
  .loi-wrap li { margin: 0 0 4px; }
  .loi-meta { margin-bottom: 14px; }
  .loi-sign { margin-top: 30px; }
  .loi-sign table { width: 100%; border-collapse: collapse; }
  .loi-sign td { width: 50%; vertical-align: top; padding-top: 24px; }
</style>

{% if letter_head_content and not no_letterhead %}
<div class="letter-head">{{ letter_head_content }}</div>
{% endif %}

<div class="loi-wrap">
  <h1>Letter of Intent</h1>

  <div class="loi-meta">
    <p>{{ frappe.utils.formatdate(doc.offer_date) if doc.offer_date else '' }}</p>
    <p><strong>{{ doc.applicant_name or '' }}</strong></p>
    <p>{{ (doc.custom_applicant_full_address or '').replace('\\n', '<br>') }}</p>
    <p>M: {{ doc.custom_applicant_phone_number or '' }}</p>
    <p><strong>Subject:</strong> Letter of Intent</p>
  </div>

  <p>Dear {{ doc.applicant_name or 'Candidate' }},</p>

  <p>
    We are pleased to express our intent to associate with you in the role of
    {{ doc.designation or '' }} at {{ doc.company or '' }}, subject to the terms outlined below
    and successful completion of the joining formalities.
  </p>

  <p>
    This Letter of Intent ("LOI") is being issued to align on role scope, territory ownership,
    and initial performance expectations before issuance of the formal Appointment Letter.
  </p>

  <h2>1. Role & Territory Allocation</h2>
  <p>
    As a {{ doc.designation or '' }}, your core mandate will be to build, grow, and stabilize the
    assigned territory.
  </p>
  <p><strong>Territory Definition:</strong><br>{{ ns.territory or '' }}</p>

  <h2>2. Key Responsibilities</h2>
  <ul>
    {% for line in (ns.responsibilities or '').split('\\n') if line.strip() %}
      <li>{{ line }}</li>
    {% endfor %}
  </ul>

  <h2>3. Commercial Understanding</h2>
  <p>
    Your compensation structure will be as per the mutually agreed terms discussed during the
    selection process.
  </p>
  <p>
    A variable performance-linked package, which shall be in addition to your fixed discussed
    component, will be shared with you along with your Formal Appointment Letter.
  </p>
  <p>
    The final compensation structure, incentive policy, and applicable benefits shall be governed
    exclusively by the terms stated in the Appointment Letter.
  </p>

  <h2>4. Sales Projection Reference</h2>
  <p>
    You have submitted a Sales Projection & Market Development Plan, which will serve as the
    baseline performance reference during your probation period.
  </p>
  <p>The following documents are attached and form part of this LOI:</p>
  <ul>
    <li>Annexure A: Your Curriculum Vitae (CV)</li>
    <li>Annexure B: Your Sales Projection shared during the interview process</li>
    <li>Annexure C: Your expected monthly sales performance</li>
  </ul>
  <p>
    Your continuation beyond probation will be evaluated against actual performance versus your
    submitted projections, along with execution discipline and market feedback.
  </p>

  <h2>5. Probation</h2>
  <p>
    Your initial association will be on a probationary period of 90 (ninety) days from your date
    of joining. Confirmation will be subject to satisfactory performance, reporting discipline,
    and cultural alignment.
  </p>

  <h2>6. Joining, Posting & Work Discipline</h2>
  <p><strong>Expected Date of Joining:</strong> {{ doc.date_of_joining or '' }}</p>
  <p><strong>Headquarter:</strong> {{ ns.headquarter or '' }}</p>
  <p>
    Your working hours will be field-driven and market-oriented. You are expected to maintain
    full-day field productivity and a market working time of 9 hours and remain available between
    10:00 AM and 7:00 PM for internal coordination, reporting, and official communication.
  </p>
  <p>
    Your first day will involve an onboarding session during which you will receive further
    information regarding your role, responsibilities, product portfolio, reporting processes,
    and territory execution framework.
  </p>

  <h2>7. Non-Binding Nature</h2>
  <p>
    This Letter of Intent is not a legally binding employment contract. The final terms of
    employment shall be governed exclusively by the Formal Appointment Letter.
  </p>

  <h2>8. Acceptance</h2>
  <p>
    If you agree with the above intent and wish to proceed, please sign and return a copy of this
    letter with the word "Accepted", along with your signature and date, within 48 hours of receipt.
  </p>

  <p>
    We look forward to having you on our team and are confident that this probationary period will
    be a valuable opportunity for both you and the Company to evaluate long-term mutual fit and
    performance alignment.
  </p>

  <div class="loi-sign">
    <table>
      <tr>
        <td>
          <p>Warm regards,</p>
          <p>For {{ doc.company or '' }}</p>
          <p>HR Team</p>
        </td>
        <td>
          <p><strong>Accepted by:</strong></p>
          <p>Name: ________________________</p>
          <p>Signature: ___________________</p>
          <p>Date: ________________________</p>
        </td>
      </tr>
    </table>
  </div>
</div>
""".strip()

	if frappe.db.exists("Print Format", name):
		doc = frappe.get_doc("Print Format", name)
		created = False
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Print Format",
				"name": name,
				"module": "Printing",
			}
		)
		created = True

	doc.doc_type = "Job Offer"
	doc.print_format_for = "DocType"
	doc.print_format_type = "Jinja"
	doc.custom_format = 1
	doc.standard = "No"
	doc.raw_printing = 0
	doc.disabled = 0
	doc.html = html

	if created:
		doc.insert(ignore_permissions=True)
	else:
		doc.save(ignore_permissions=True)

	doctype_meta = frappe.get_meta("DocType")
	if doctype_meta.has_field("default_print_format"):
		frappe.db.set_value(
			"DocType",
			"Job Offer",
			"default_print_format",
			name,
			update_modified=False,
		)

	print_format_meta = frappe.get_meta("Print Format")
	if print_format_meta.has_field("default"):
		frappe.db.set_value(
			"Print Format",
			name,
			"default",
			1,
			update_modified=False,
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
