from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='savetweets',
    version='1.0.0',
    description='A simple program to archive tweets to the Internet Archive.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['snscrape','tqdm','requests'],
    author='nisotsu',
    url='https://github.com/nisotsu/SaveTweets',
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['savetweets = savetweets.savetweets:main'],
    }
)