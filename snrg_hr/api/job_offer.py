import frappe
from frappe.model.naming import make_autoname
from frappe.utils import getdate, today


COMPANY_CODE_MAP = {
	"SNRG Electricals India Private Limited": "SEI",
	"SNRG Wires India Private Limited": "SWI",
}


def validate(doc, method=None):
	apply_naming_metadata(doc)


def autoname(doc, method=None):
	apply_naming_metadata(doc)
	doc.name = make_autoname(doc.custom_naming_series)


def before_insert(doc, method=None):
	apply_naming_metadata(doc)


def apply_naming_metadata(doc):
	doc.custom_company_code = _get_company_code(doc.company)
	doc.custom_fy_short = _get_fy_short(doc.offer_date)
	doc.custom_naming_series = _build_naming_series(doc.custom_company_code, doc.custom_fy_short)


def _get_company_code(company):
	return COMPANY_CODE_MAP.get(company or "", "SNRG")


def _get_fy_short(offer_date):
	date_obj = getdate(offer_date or today())
	fy_start = date_obj.year
	if date_obj.month < 4:
		fy_start -= 1
	return str(fy_start + 1)[-2:]


def _build_naming_series(company_code, fy_short):
	return f"SNRG/HR/OL/{company_code}/{fy_short}/.###"
