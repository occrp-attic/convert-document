from setuptools import setup, find_packages

setup(
    name='unoservice',
    version='1.0.7',
    long_description="LibreOffice PDF conversion servi ce.",
    author='Organized Crime and Corruption Reporting Project',
    author_email='pudo@occrp.org',
    url='https://tech.occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    package_data={},
    zip_safe=False,
    install_requires=[],
    test_suite='nose.collector',
    entry_points={},
    tests_require=['coverage', 'nose']
)
