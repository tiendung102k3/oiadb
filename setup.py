from setuptools import setup, find_packages

setup(
    name="oiadb",
    version="0.6.1", # Added multiplatform support, auto ADB installation
    packages=find_packages(where='oiadb_package'),
    package_dir={'': 'oiadb_package'},
    description="ADB Python wrapper library with enhanced functionality, image recognition and multiplatform support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tien Dung",
    author_email="example@example.com",
    url="https://github.com/tiendung102k3/oiadb",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    keywords="adb, android, debug, bridge, automation, testing, image recognition, opencv, uiautomator, multiplatform, windows, linux, macos, termux",
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.20",
    ],
    extras_require={
        "image": [
            "opencv-python>=4.5.0",
            "numpy>=1.19.0",
        ]
    },
    include_package_data=True,
    package_data={},
    project_urls={
        "Bug Reports": "https://github.com/tiendung102k3/oiadb/issues",
        "Source": "https://github.com/tiendung102k3/oiadb",
    },
)
