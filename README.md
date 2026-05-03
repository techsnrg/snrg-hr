# SNRG HR

Custom ERPNext and Frappe app for SNRG HR process automation, starting with automated job offer and appointment letter workflows.

## Scope

- Job offer automation based on SNRG templates
- Appointment letter support
- HR-specific custom fields, print formats, and workflows
- Reusable services for future HR enhancements

## App Name

- Python package: `snrg_hr`
- Desk module: `SNRG HR`

## Install

From your bench:

```bash
bench get-app <repo-url>
bench --site <your-site> install-app snrg_hr
bench --site <your-site> migrate
```

## Status

Initial scaffold created. Functional HR features will be added incrementally.
