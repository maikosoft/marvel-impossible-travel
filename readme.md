
## Marvel Impossible Travel Code Assessment

This repository is a code assessment for Collage Group.

### Requirements
git, Docker, python 3.9, pip

## Installation

Clone this repo and move to the folder:
```sh
git clone <this-repository-url>
cd ./marvel-back
```

Create a ".env" file and write the API keys:

```sh
DATABASE=data/marvel.db
API_URL=http://gateway.marvel.com/v1/public
API_PUBLIC_KEY=<YOUR-MARVEL-PUBLIC-KEY>
API_PRIVATE_KEY=<YOUR-MARVEL-PRIVATE-KEY>
API_LIMIT=100
```

Run docker container:

```sh
docker-compose up
```

Open web browser with the url:

```sh
http://localhost/
```
