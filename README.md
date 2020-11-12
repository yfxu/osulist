# osulist #

Flask app for creating and sharing osu! beatmap playlists.

## Setup ##

1. clone this repository
    ```bash
    git clone git@github.com:yfxu/osulist.git
    cd osulist
    ```
    
2. setup virtual environment and install dependencies
    ```bash
    python3 -m venv env
    source /env/bin/activate
    pip install -r requirements.txt
    ```

3. create a MongoDB atlas cluster online at https://www.mongodb.com/cloud/atlas
    1. create a public user with read & write access to the cluster
    2. configure the network access to grant database access to your machine

4. create a new OAuth application in your osu! account settings
    https://osu.ppy.sh/home/account/edit

5. setup environment variables
    1. create a `.env` file in
        ```bash
        touch .env
        ```
    2. add the following variables to your `.env` file
        ```
        APP_SECRET_KEY=<some hard-to-guess string>
        MONGO_URI=<your MongoDB connection string>
        OSU_TOKEN=<your osu! api v1 token>
        OSU_CLIENT_SECRET=<osu! OAuth application client secret>
        OSU_CLIENT_ID=<osu! OAuth application 4-digit client ID>
        BASE_URL=<url where your application will be hosted>
        ```
        
6. start development server
    ```
    python osulist.py
    ```

## Postscript ##
Please play my osu! beatmaps