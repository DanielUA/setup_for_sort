from setuptools import setup

setup(
    name='sort_for_folders',
    version='0.0.2',
    description='Use for sorting files in folders',
    author="Danyil",
    url='https://github.com/DanielUA/domashka_6',
    author_email='tishakovdanyil@gmail.com',
    license='MIT',
    classifiers=[],
    packages=['clean_folder'],
    data_files=[("clean_folder", ["clean_folder/clean_folder"])],
    include_package_data=True,
    install_requires=['markdown'],
    entry_points={'console_scripts': ['sorter = clean_folder.clean:sorter']},
)