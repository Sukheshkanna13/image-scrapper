scrapper1.py - worksover API based fetch execute cycle 

whereas scrapper.py - works just based on reading the HTML file, where it inolves manual pasting of HTML skeleton code into this file from zyte.com

scrapper2.py - "srcset" (which typically lists multiple image URLs with their resolutions), the code now selects the candidate with the highest multiplier 
output images are stored under the folder (downloaded_images)

Improvisations
=> high resolution images to be needed for scrapped data, so make sure to attain its original image, rather than thumbnail image as of whole 
=>when runned, multiple times the code resturn output images in the same directory, resulting in confusion, so better to alter the code to create new directories for each run (resuting in low confusion)