from setuptools import find_packages, setup

setup(
    name='scrapy_cr_justice_gov_lb',
    packages=find_packages(),
    version='0.0.4',
    description='scrapy spider for cr.justice.gov.lb',
    author='Shadi Akiki',
    license='BSD-3',
    install_requires = [
      "Scrapy==1.5.0",
      "pandas==0.22.0",
      "google-cloud-translate==1.3.1",
      "beautifulsoup4==4.6.0",
    ]
)
