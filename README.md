# hypnotube-downloader
A basic Python script to download videos from Hypnotube. This script will download a video from Hypnotube and convert it so that the metadata (title, author, thumbnail) are embedded directly into the downloaded file. Useful for looping over a list of Hypnotube videos you have accumulated that you wish to download in bulk.

# Prerequisites
* ffmpeg must be installed on the system running this script.
* The following Python packages are required: **argparse, requests, os, tqdm, bs4 (BeautifulSoup)**

# Usage
Usage of the script is fairly straightforward:
```
python htube.py https://example.com/url-to-hypnotube-video
```
