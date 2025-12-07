# crafty-4 Resource Menager
### menager for crafty controler v4 adds a new tab to each server dashboard, which can be used to download plugins/mods/resourcepacks directly in your panel using modrinth api.
## Setup guide:
### 1. Get your api key from modrinth
To get your own API key you need to go [this site](https://docs.modrinth.com/api/) and follow the instructions of generatin your own token
### 2. Setting up files
Modify your files as show on repo, use the same file hierarchy and follow comented instructions inside files

**!!!IMPORTANT!!!**
DO NOT JUST REPLACE FILES CHECK INSIDE FILE WHAT YOU NEED TO ADD!!!

### 3. Restarting crafty and if using reverse proxy nginx/apache
```
find templates -name "__pycache__" -type d -exec rm -rf {} +
sudo systemctl restart crafty
```
### 4. Enjoy!!!
Thats all now u can install plugins/mod from your panel.