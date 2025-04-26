from setuptools import setup, find_packages

setup(
    name='my_adb_lib',
    version='0.2.0',
    packages=find_packages(),
    description='ADB Python wrapper library with enhanced functionality',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tien Dung',
    author_email='example@example.com',
    url='https://github.com/yourusername/my-adb-lib',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='adb, android, debug, bridge, automation, testing',
    python_requires='>=3.6',
    install_requires=[],
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/my-adb-lib/issues',
        'Source': 'https://github.com/yourusername/my-adb-lib',
    },
)
