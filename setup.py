from setuptools import find_namespace_packages, setup
setup(name='canvas',
      version='0.1',
      packages = find_namespace_packages(where="src"),
      package_dir = {"": "src"},
      # include_package_data=True,
      package_data={
          "canvas.patterns" : ["*.txt"],
          },
      install_requires=[
          'pyclipper',
          ]
      )
