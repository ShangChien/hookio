from setuptools import setup, find_packages

setup(
    name='hookio',  # 包的名称
    version='0.0.7',          # 版本号
    description='the coding style of hook',
    long_description=open('README.md').read(),  # 长描述
    long_description_content_type="text/markdown",
    author='ShangChien',
    author_email='hi@emm.sh',
    url='https://github.com/ShangChien/hookio',
    packages=find_packages(),  # 自动查找包
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.10',
)