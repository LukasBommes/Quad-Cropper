import sys
from os.path import dirname, realpath
from setuptools import setup, find_packages

name = "src"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)

setup(
    name="Quad-Cropper",
    maintainer="Lukas Bommes",
    url='https://github.com/LukasBommes/Quad-Cropper',
    version="0.1", 
    packages=find_packages(),   
    package_dir={name: name},    
    include_package_data=True,
    license="MIT",
    description="Desktop app for cropping and rectifying quadrilaterals from images.",
    install_requires=[
        "numpy>=1.19.1,<2",
        "opencv-python>=4.2.0.34,<5",
        "PySide6>=6.2.1,<7",
    ],
    python_requires='>=3.8, <4',
    entry_points={"gui_scripts": ['quadcropper = src.__main__:main']},
    keywords=["quadcropper", "desktop-app", "image", "crop", 
              "perspective", "crop-image", "homography", 
              "recitfy", "pyside6"
              ],
    classifiers=['Operating System :: OS Independent',
                'Programming Language :: Python :: 3',
                ],
    platforms=['ALL']
)
