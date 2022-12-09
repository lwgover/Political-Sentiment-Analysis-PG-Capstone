import urllib.request
from bs4 import BeautifulSoup

#===============================================================================================================================================================
class Bill:
    def __init__(self,title:str, text:str, sponsor:str, cosponsors:list):
        self.title = title
        self.text = text
        self.sponsor = sponsor
        self.cosponsors = cosponsors
    def __str__(self):
        string = "Title: " + self.title
        string += '\nSponsor: ' + self.sponsor
        string += '\nCosponsors: ' + str(self.cosponsors)
        string += '\nBill:\n' + self.text
        return string
#===============================================================================================================================================================

def congressSearchURL_to_names(bill_url:str) -> str:

        html = get_html(bill_url)
        start_index = html.find("body")
        start_index = start_index + html[start_index:].find("container")
        start_index = start_index + html[start_index:].find("search-row")
        start_index = start_index + html[start_index:].find("basic-search-results-lists")
        names = []
        while html[start_index:].find("expanded") >= -1:
            try:
                start_index = start_index + html[start_index:].find("expanded") + len("expanded")
                start_index = start_index + html[start_index:].find("/member/") + len("/member/")
                end_index = start_index + html[start_index:].find("/")
                first_and_last = html[start_index:end_index].split('-')
                names.append(first_and_last[0] + " " + first_and_last[1])
            except IndexError as e:
                break
        return names

def congressSearchURL_to_party(bill_url:str) -> str:

        html = get_html(bill_url)
        start_index = html.find("body")
        start_index = start_index + html[start_index:].find("container")
        start_index = start_index + html[start_index:].find("search-row")
        parties = []
        while html[start_index:].find("member-profile") >= -1:
            try:
                start_index = start_index + html[start_index:].find("member-profile")
                start_index = start_index + html[start_index:].find("Party:")
                if html[start_index:].find("Party:") == -1:
                    break
                start_index = start_index + html[start_index:].find("<span>") + len("<span>")
                end_index = start_index + html[start_index:].find("</span>")
                print(html[start_index:end_index])
                if len(html[start_index:end_index]) > 15:
                    break
                parties.append(html[start_index:end_index])
            except IndexError as e:
                break
        return parties

def congressSearchURL_to_states(bill_url:str) -> str:

        html = get_html(bill_url)
        start_index = html.find("body")
        start_index = start_index + html[start_index:].find("container")
        start_index = start_index + html[start_index:].find("search-row")
        states = []
        while html[start_index:].find("member-profile") >= -1:
            try:
                start_index = start_index + html[start_index:].find("member-profile")
                start_index = start_index + html[start_index:].find("State:")
                if html[start_index:].find("State:") == -1:
                    break
                start_index = start_index + html[start_index:].find("<span>") + len("<span>")
                end_index = start_index + html[start_index:].find("</span>")
                print(html[start_index:end_index])
                if len(html[start_index:end_index]) > 15:
                    break
                states.append(html[start_index:end_index])
            except IndexError as e:
                break
        return states


def congressSearchURL_to_districts(bill_url:str) -> str:

        html = get_html(bill_url)
        start_index = html.find("body")
        start_index = start_index + html[start_index:].find("container")
        start_index = start_index + html[start_index:].find("search-row")
        districts = []
        while html[start_index:].find("member-profile") >= -1:
            try:
                start_index = start_index + html[start_index:].find("member-profile")
                start_index = start_index + html[start_index:].find("District:")
                if html[start_index:].find("District:") == -1:
                    break
                start_index = start_index + html[start_index:].find("<span>") + len("<span>")
                end_index = start_index + html[start_index:].find("</span>")
                print(html[start_index:end_index])
                if len(html[start_index:end_index]) > 15:
                    break
                districts.append(html[start_index:end_index])
            except IndexError as e:
                break
        return districts

def get_html(bill_url:str) -> str:
    try:
        url = bill_url
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        page = opener.open(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        return html
    except urllib.error.URLError as e:
        print(e.reason)
        print(":(")


#===============================================================================================================================================================
if __name__ == "__main__":
    url = 'https://www.congress.gov/members?q=%7B%22congress%22%3A117%7D'
    print(congressSearchURL_to_districts(url))