from plistlib import InvalidFileException


class Bill:
    def __init__(self, title:str, sponsor, cosponsors:list, text:str, file_location:str):
        self.title = title
        self.sponsor = sponsor
        self.cosponsors = cosponsors
        self.text = text
        self.party = self.sponsor.party
        self.file_location = file_location

    def __init__(self, file:str):
        self.title, self.sponsor, self.cosponsors, self.text, self.party = self.parse_file(file)
        self.file_location = file

    def parse_file(self, file:str):
        with open (file, "r") as billtxt:
            try:
                data = billtxt.read()
            except UnicodeDecodeError as e:
                raise InvalidFileException("File wasn't functional")
                
        splits = data.split('&&&')
        title = splits[0]
        if len(splits[1]) <= 0:
            return title, None, [], splits[2], 'N/A'
        sponsors = splits[1].split('\n')
        sponsors = list(filter(lambda x: len(x) > 5, sponsors))
        sponsor = CongressPerson(sponsors[0])
        cosponsors = list(map(CongressPerson, sponsors[1:]))
        text = splits[2]
        party = sponsor.party
        return title, sponsor, cosponsors, text, party
    
    def percent_left(self):
        num_dem = 0
        if self.sponsor == None:
            return 0
        if self.sponsor.party == 'D':
            num_dem += 1

        if self.cosponsors == []:
            return num_dem
        for cosponsor in self.cosponsors:
            if cosponsor.party == 'D':
                num_dem += 1
        return num_dem / (1 + len(self.cosponsors))

    def percent_right(self):
        num_rep = 0
        if self.sponsor == None:
            return 0
        if self.sponsor.party == 'R':
            num_rep += 1

        if self.cosponsors == []:
            return num_rep
        for cosponsor in self.cosponsors:
            if cosponsor.party == 'R':
                num_rep += 1
        return num_rep / (1 + len(self.cosponsors))

    def percent_independent(self):
        num_ind = 0
        if self.sponsor == None:
            return 0
        if self.sponsor.party == 'I':
            num_ind += 1

        if self.cosponsors == []:
            return num_ind
        for cosponsor in self.cosponsors:
            if cosponsor.party == 'I':
                num_ind += 1
        return num_ind / (1 + len(self.cosponsors))

class CongressPerson:
    def __init__(self, full_name, party, state):
        self.full_name = full_name
        self.party = party
        self.state = state

    def __init__(self, string):
        self.full_name, self.party, self.state = self.parse_str(string)

    def parse_str(self, string:str):
        splits = string.split('\t')
        return splits[0], splits[1], splits[2]