from setuptools import find_packages, setup


with open("requirements.txt") as f:
	install_requires = [line for line in f.read().splitlines() if line.strip()]


	setup(
	name="snrg_hr",
	version="0.0.1",
	description="Custom ERPNext HR automation for SNRG Electricals",
	author="SNRG Electricals",
	author_email="admin@snrgelectricals.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
