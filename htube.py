import argparse
import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
# Set up command-line arguments.
parser = argparse.ArgumentParser(description='Download and process a video from a URL')
parser.add_argument('url', help='The URL of the video')
args = parser.parse_args()

url = args.url
print(f"Parsing link: {url}...")
# Download the HTML of the URL passed to the script.
response = requests.get(url)
# If we don't get a 200, 301 or 302 response:
if response.status_code not in [200, 301, 302]:
    raise requests.exceptions.HTTPError(f"{response.status_code} - Error fetching URL")
    
# Store the HTML of the page in question in a variable.
html = response.text

# Use BeautifulSoup to extract information from the HTML elements on the page:
soup = BeautifulSoup(html, 'html.parser')
poster = soup.find('meta', {'property': 'og:image'})['content']
src = soup.find('source')['src']
h1_text = soup.find('h1').text
user_name = soup.find('span', {'class': 'user-name'}).text.replace('Submitted by', '').strip()
desc = soup.find('div', {'class': 'main-description'}).text.strip()

# Create a filename in the format 'Uploader - Video Title':
filename = user_name + " - " + h1_text

print("Link parsed successfully.")

# Create a variable for checking if the file has already been downloaded previously:
filename_to_check = filename + ".mp4"

# If the file already exists in the folder:
if os.path.isfile(filename_to_check):
    # Skip the file and do no further processing.
    print(f"{filename} appears to have already been downloaded, skipping.")
else:
    print(f"Downloading {h1_text} by {user_name} from Hypnotube...")
    print("Downloading video...")
    # Download the src file with progress bar.
    src_filename = f"{filename}_temp.mp4"
    try:
        src_response = requests.get(src, stream=True)
        src_response.raise_for_status()
    # If the link is dead:
    except requests.exceptions.HTTPError:
        # Log errors to 'herrors.txt'
        with open("herrors.txt", "a") as f:
            f.write(f"Error downloading {src}\n")
        # Terminate the script.
        raise
    # Download the file with a fancy progress bar.
    total_size = int(src_response.headers.get('content-length', 0))
    block_size = 1024
    with open(src_filename, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=src_filename) as pbar:
            for data in src_response.iter_content(block_size):
                f.write(data)
                pbar.update(len(data))
                
    # Download the thumbnail with progress bar
    poster_filename = f"{filename}_temp.jpg"
    try:
        poster_response = requests.get(poster, stream=True)
        poster_response.raise_for_status()
    # If the link is dead:
    except requests.exceptions.HTTPError:
        # Log errors to 'herrors.txt'
        with open("herrors.txt", "a") as f:
            f.write(f"Error downloading {poster}\n")
        # Terminate the script.
        raise
    # Download the file with a fancy progress bar.
    total_size = int(poster_response.headers.get('content-length', 0))
    block_size = 1024
    with open(poster_filename, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=poster_filename) as pbar:
            for data in poster_response.iter_content(block_size):
                f.write(data)
                pbar.update(len(data))
                
    print("Injecting metadata into new MP4 file...")
    # Run an ffmpeg command to create the final file.
    cmd = f'ffmpeg -nostdin -hide_banner -loglevel error -i "{src_filename}" -i "{poster_filename}" -metadata title="{h1_text}" -metadata author="{user_name}" -metadata composer="{user_name}" -metadata album_artist="{user_name}" -metadata description="{desc}" -metadata comment="{desc}" -map 0 -map 1 -c copy -c:v:1 png -disposition:v:1 attached_pic "{filename}.mp4"'
    os.system(cmd)
    print("Cleaning up temporary files...")
    # Delete the temporary files.
    os.remove(src_filename)
    os.remove(poster_filename)
    print(f"File downloaded successfully to {filename}.mp4!")