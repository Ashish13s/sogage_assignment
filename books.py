import json
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


class GoogleBooksAPI:
    def __init__(self):
        self.base_url: str = "https://www.googleapis.com/books/v1/volumes"

    def get_params(self, search_query: str) -> Dict[str, str]:
        params: Dict[str, str] = {
            "q": search_query,
            "printType": "books",
            "projection": "lite",
            "+": "intitle",
            "key": str(os.getenv("API_KEY")),
        }
        return params

    def get_response(self, search_query: str) -> Dict[str, Any]:
        params: Dict[str, str] = self.get_params(search_query)
        try:
            response: requests.models.Response = requests.get(
                self.base_url, params=params
            )
            return response.json()
        except Exception as e:
            print(e)
        return {}

    def get_books(self, search_query: str) -> List[Dict[str, Any]]:
        response_json: Dict[str, Any] = self.get_response(search_query)
        all_books: List[Dict[str, Any]] = []
        if "items" in response_json:
            books: List[Dict[str, Any]] = response_json["items"]
            for book in books:
                book_info: Dict[str, Any] = book["volumeInfo"]
                all_books.append(book_info)
        return all_books

    def format_for_json(self, books) -> List[Dict[str, str]]:
        formatted_books: List[Dict[str, str]] = []
        for book in books:
            formatted_book: Dict[str, str] = {}
            formatted_book["Title"] = book.get("title", "")
            formatted_book["Content"] = book.get("description", "")
            formatted_books.append(formatted_book)
        return formatted_books


class WikiBooksAPI:
    def __init__(self) -> None:
        self.base_url = "https://en.wikibooks.org/w/api.php"

    def get_params(self, search_query: str) -> Dict[str, str]:
        params: Dict[str, str] = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srlimit": "50",
        }
        return params

    def get_response(self, search_query: str) -> Dict[str, Any]:
        params: Dict[str, str] = self.get_params(search_query)
        try:
            response: requests.models.Response = requests.get(
                self.base_url, params=params
            )
            return response.json()
        except Exception as e:
            print(e)
        return {}

    def get_books(self, search_query: str) -> List[Dict[str, Any]]:
        response_json = self.get_response(search_query)
        all_books = []
        if "search" in response_json["query"]:
            books = response_json["query"]["search"]
            for book in books:
                formatted_book = self.format_response(book)
                all_books.append(formatted_book)
        return all_books

    def format_response(self, response) -> Dict[str, Any]:
        response["snippet"] = response["snippet"].replace(
            '<span class="searchmatch">', ""
        )
        response["snippet"] = response["snippet"].replace("</span>", "")
        return response

    def format_for_json(self, books) -> List[Dict[str, str]]:
        formatted_books = []
        for book in books:
            formatted_book = {}
            formatted_book["Title"] = book.get("title", "")
            formatted_book["Content"] = book.get("snippet", "")
            formatted_books.append(formatted_book)
        return formatted_books


def print_books(all_books: List[Dict[str, Any]]) -> None:
    for book in all_books:
        print(json.dumps(book, indent=2))


def write_to_json(
    google_books: List[Dict[str, str]], wiki_books: List[Dict[str, str]]
) -> None:
    file_name = "output.json"
    with open(file_name, "w") as f:
        google_books.extend(wiki_books)
        json.dump({"books": google_books}, f, indent=2)


if __name__ == "__main__":
    load_dotenv()
    google_books: GoogleBooksAPI = GoogleBooksAPI()
    wiki_books: WikiBooksAPI = WikiBooksAPI()
    search_query: str = input("Enter search string: ")
    g_books: List[Dict[str, Any]] = google_books.get_books(search_query)
    w_books: List[Dict[str, Any]] = wiki_books.get_books(search_query)
    print("**************************************************")
    print("Google Books API\n\n")
    print_books(g_books)
    print("**************************************************")
    print("Wiki Books API\n\n")
    print_books(w_books)
    print("**************************************************")
    write_to_json(
        google_books.format_for_json(g_books),
        wiki_books.format_for_json(w_books),
    )
