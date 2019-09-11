import json

class UPSObject:
    def __init__(self,jsonFile):
        self.__parse_data(jsonFile)

    def __parse_data(self,jsonFile):
        with open(jsonFile) as file:
            data = json.load(file)
            for var in data.keys():
                self.timesteps = data[var]['timesteps']
                varName = self.__2str(var,'-')
                setattr(self, varName+"_error", data[var]['error'])

    def __2str(self,str,delimiter):
        splitStr = str.split(delimiter)
        separator = "_"
        return separator.join(splitStr)
