# a REST client
# When writing our OMDb client, we’ll try to stick to these rules:
# Have a single method that’s used to make requests, so we have just one place to add authentication and error handling.
# It should not need to know about Django at all, this will allow us to refactor more easily and re-use the code in a non-Django project.
# The transformation from JSON to Python should take place in the client. The consumers of the client should not need to know about the data structure of the response.
# This means our API can change and only our client code needs to be updated, not different parsing code throughout our codebase.


import logging

import requests

logger = logging.getLogger(__name__)


# Another option could be to define the API URL in the Django settings. 
# You'd probably prefer this if the API you were working with had both dev and production URLs.
# Since OMDb doesn't and we don't expect it to change, we'll just leave it set here.
OMDB_API_URL = "https://www.omdbapi.com/"

class OmdbMovie:
    """A simple class to represent movie data coming back from OMDb
    and transform to Python types."""

# We’re moving all the transformations from API to Python into a single place. 
# There is a separation between the data that’s returned from the API and how we’re using said data in Python.
    def __init__(self, data):
        """Data is the raw JSON/dict returned from OMDb"""
        self.data = data

    def check_for_detail_data_key(self, key):
        """Some keys are only in the detail response, raise an
        exception if the key is not found."""
        
        if key not in self.data:
            raise AttributeError(
                f"{key} is not in data, please make sure this is a detail response."
            )

    @property
    def imdb_id(self):
        return self.data["imdbID"]

    @property
    def title(self):
        return self.data["Title"]

    @property
    def year(self):
        return int(self.data["Year"])

    @property
    def runtime_minutes(self):
        self.check_for_detail_data_key("Runtime")

        rt, units = self.data["Runtime"].split(" ")

        if units != "min":
            raise ValueError(f"Expected units 'min' for runtime. Got '{units}")

        return int(rt)

    @property
    def genres(self):
        self.check_for_detail_data_key("Genre")

        return self.data["Genre"].split(", ")

    @property
    def plot(self):
        self.check_for_detail_data_key("Plot")
        return self.data["Plot"]

# Here’s an example of how it would be used:        
# data is a dictionary from the API
# >>> data = {"Title": "My Great Movie", "Year": "1991"}
# >>> movie = OmdbMovie(data)
# >>> movie.title
# 'My Great Movie'        


class OmdbClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def make_request(self, params):
        """Make a GET request to the API, automatically adding the `apikey` to parameters."""
        params["apikey"] = self.api_key

        resp = requests.get(OMDB_API_URL, params=params)
        resp.raise_for_status()
        return resp

    def get_by_imdb_id(self, imdb_id):
        """Get a movie by its IMDB ID"""
        logger.info("Fetching detail for IMDB ID %s", imdb_id)
        resp = self.make_request({"i": imdb_id})
        return OmdbMovie(resp.json())

    def search(self, search):
        """Search for movies by title. This is a generator so all results from all pages will be iterated across."""
        page = 1
        seen_results = 0
        total_results = None

        logger.info("Performing a search for '%s'", search)

        while True:
            logger.info("Fetching page %d", page)
            resp = self.make_request({"s": search, "type": "movie", "page": str(page)})
            resp_body = resp.json()
            if total_results is None:
                total_results = int(resp_body["totalResults"])

            for movie in resp_body["Search"]:
                seen_results += 1
                yield OmdbMovie(movie)

            if seen_results >= total_results:
                break

            page += 1