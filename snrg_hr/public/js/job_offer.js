function set_company_code(frm) {
	const companyMap = {
		"SNRG Electricals India Private Limited": "SEI",
		"SNRG Wires India Private Limited": "SWI",
	};

	const company = frm.doc.company || "";
	frm.set_value("custom_company_code", companyMap[company] || "SNRG");
}

function set_fy_short(frm) {
	const dateValue = frm.doc.offer_date || frappe.datetime.get_today();
	const d = frappe.datetime.str_to_obj(dateValue);
	if (!d) return;

	let fyStart = d.getFullYear();
	if (d.getMonth() + 1 < 4) {
		fyStart -= 1;
	}

	const fyShort = String(fyStart + 1).slice(-2);
	frm.set_value("custom_fy_short", fyShort);
}

function set_custom_naming_series(frm) {
	const companyCode = frm.doc.custom_company_code || "SNRG";
	const fyShort = frm.doc.custom_fy_short || "";
	if (!fyShort) return;

	frm.set_value("custom_naming_series", `SNRG/HR/OL/${companyCode}/${fyShort}/.###`);
}

function refresh_naming_fields(frm) {
	set_company_code(frm);
	set_fy_short(frm);
	set_custom_naming_series(frm);
}

frappe.ui.form.on("Job Offer", {
	onload(frm) {
		if (frm.is_new()) {
			refresh_naming_fields(frm);
		}
	},

	refresh(frm) {
		if (frm.is_new()) {
			refresh_naming_fields(frm);
		}
	},

	company(frm) {
		refresh_naming_fields(frm);
	},

	offer_date(frm) {
		refresh_naming_fields(frm);
	},

	before_save(frm) {
		refresh_naming_fields(frm);
	},
});
