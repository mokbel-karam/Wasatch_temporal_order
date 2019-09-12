import json

class UPSObject:
    def __init__(self,jsonFile):
        self.vars = []
        self.__parse_data(jsonFile)
    def __parse_data(self,jsonFile):
        with open(jsonFile) as file:
            data = json.load(file)
            for var in data.keys():
                if var == "timesteps":
                    setattr(self,var,data[var])
                else:
                    varName = self.__2str(var,'-')
                    varName += "_error"
                    setattr(self, varName, data[var]['error'])
                    self.vars.append(varName)

    def __2str(self,str,delimiter):
        splitStr = str.split(delimiter)
        separator = "_"
        return separator.join(splitStr)


class UPSGroup:
    def __init__(self, files):
        self.names=[]
        for file in files:
            name = file.split('.')[0]
            obj = UPSObject(file)
            setattr(self,name,obj)
            self.names.append(name)
        self.__get_clean_data()

    def __get_vars(self):
        varDicts={}
        for name in self.names:
            obj=getattr(self,name)
            varDicts[name]=obj.vars

        return varDicts

    def __get_common_vars(self):
        varDicts =self.__get_vars()
        keys = [*varDicts]
        varOld=varDicts[keys[0]]
        for num,key in enumerate(keys[1:]):
            varNew = varDicts[key]

            result = any(elem in varNew for elem in varOld )

            if result ==False:
                varOld = varNew

        return varOld

    def __get_clean_data(self):
        self.commonVars = self.__get_common_vars()
        for var in self.commonVars:
            setattr(self,var,{})
            for name in self.names:
                obj=getattr(self,name)
                dict= getattr(self,var)
                dict[name]=(obj.timesteps,getattr(obj,var))