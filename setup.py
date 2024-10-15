from ast import literal_eval
from os.path import dirname, join
from setuptools import setup


with open(join(dirname(__file__), 'post_office/version.txt')) as fh:
    VERSION = '.'.join(map(str, literal_eval(fh.read())))


setup(
    name='django-post_office',
    version=VERSION,
    author='Selwin Ong',
    author_email='selwin.ong@gmail.com',
    packages=['post_office'],
    url='https://github.com/ui/django-post_office',
    license='MIT',
    description='A Django app to monitor and send mail asynchronously, complete with template support.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README.rst']},
    python_requires='>=3.9',
    install_requires=[
        'django>=4.2',
        'django-ckeditor>=6.7.0',
        'lxml>=5.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Communications :: Email',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
