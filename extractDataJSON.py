import json
from decimal import *
import os.path 

DicoTypeOfData = {
    1 : ["IntegerFile","fort.44_BIN"],
    2 : ["FloatFile","fort.45_BIN"],
    3 : ["DoubleFile","fort.46_BIN"],
    4 : ["StringFile","fort.47_BIN"],
    5 : ["BooleanFile","fort.48_BIN"]
}

DicoTypeByData = {
    "CGCPERTE" : 2,
    "UNOMINAL" : 1,
    "MODECALC" : 1,
    "NBMAXMIT" : 1,
    "NBMAXCUR" : 1,
    "COUTECAR" : 1,
    "RELPERTE" : 1,
    "SEUILPER" : 1,
    "COUTDEFA" : 1,
    "MAXSOLVE" : 1,
    "TDPENALI" : 2,
    "HVDCPENA" : 2,
    "PROBAINC" : 2,
    "TRUTHBAR" : 5,
    "TESTITAM" : 5,
    "INCNOCON" : 5,
    "PARNOCON" : 5,
    "PAREQUIV" : 5,
    "COUENDCU" : 2,
    "COUENECU" : 2,
    "LIMCURGR" : 1,
    "ADEQUAOF" : 1,
    "REDISPOF" : 1,
    "NBTHREAT" : 1,
    "EQUILRES" : 5,
    "REDISRES" : 5,
    "VARMARES" : 5,
    "LCCVMRES" : 5,
    "LOSSDETA" : 5,
    "OVRLDRES" : 5,
    "CGNBREGI" : 1,
    "CGNOMREG" : 4,
    "TNNBNTOT" : 1,
    "ECNBCONS" : 1,
    "TNNOMNOE" : 4,
    "TNNEUCEL" : 1,
    "CPPOSREG" : 1,
    "ESAFIACT" : 1,
    "TNVAPAL1" : 1,
    "TNVACOU1" : 2,
    "TRNBGROU" : 1,
    "TRNOMGTH" : 4,
    "TNNEURGT" : 1,
    "SPPACTGT" : 2,
    "TRVALPMD" : 2,
    "TRPUIMIN" : 2,
    "TRNBTYPE" : 1,
    "TRNOMTYP" : 4,
    "TRTYPGRP" : 1,
    "SPIMPMOD" : 1,
    "TRDEMBAN" : 2,
    "CQNBQUAD" : 1,
    "CQNOMQUA" : 4,
    "CQADMITA" : 2,
    "CQRESIST" : 2,
    "QASURVDI" : 1,
    "QASURNMK" : 1,
    "TNNORQUA" : 1,
    "TNNEXQUA" : 1,
    "NBOPEBRA" : 1,
    "OPENBRAN" : 1,
    "DTNBTRDE" : 1,
    "DTTRDEQU" : 1,
    "DTMODREG" : 1,
    "DTVALINF" : 2,
    "DTVALSUP" : 2,
    "DTVALDEP" : 2,
    "DCNBLIES" : 1,
    "DCNOMQUA" : 4,
    "DCNORQUA" : 1, 
    "DCNEXQUA" : 1,
    "DCMINPUI" : 2,
    "DCMAXPUI" : 2,
    "DCIMPPUI" : 2,
    "DCREGPUI" : 1,
    "DCTENSCD" : 2,
    "DCRESIST" : 2,
    "DCPERST1" : 2,
    "DCPERST2" : 2,
    "DCNDROOP" : 1,
    "DCDROOPK" : 2,
    "DMNBDEFK" : 1,
    "DMNOMDEK" : 4,
    "DMPTDEFK" : 1,
    "DMDESCRK" : 1,
    "NBDEFRES" : 1,
    "PTDEFRES" : 1,
    "DTNBDEFK" : 1,
    "DTPTDEFK" : 1, 
    "DCNBDEFK" : 1,
    "DCPTDEFK" : 1,
    "NBLDCURA" : 1,
    "LDNBDEFK" : 1,
    "LDNBDEFK" : 1,
    "LDCURPER" : 1,
    "LDPTDEFK" : 1,
    "GRNBCURA" : 1,
    "GRNBDEFK" : 1,
    "GRPTDEFK" : 1,
    "SECTNBSE" : 1,
    "SECTNOMS" : 4,
    "SECTMAXN" : 2,
    "SECTNBQD" : 1,
    "SECTTYPE" : 1,
    "SECTNUMQ" : 1,
    "SECTCOEF" : 2,
    "NBGBINDS" : 1,
    "NBLBINDS" : 1,
    "GBINDDEF" : 1,
    "GBINDNOM" : 4,
    "GBINDREF" : 1,
    "LBINDDEF" : 1,
    "LBINDNOM" : 4,
    "NBVARMAR" : 1,
    "PTVARMAR" : 1,
    "RAZGROUP" : 5
}

def searchForData(dataJSON:dict, dataName:str)->list:
    """Returns the list of data desginated by the name 'dataName' in a fort.JSON
    @Param dataJSON : the imported content of the JSON file
    @Param dataName : the name of the data we want to access (ex : 'SECTNBSE' for the number of watched sections)
    @Return : the list of the data"""

    if dataName not in DicoTypeByData : raise Exception(f'{dataName} not found in the usual list of fort.JSON section name')
    typeOfData = DicoTypeOfData[DicoTypeByData[dataName]]
    for i in range(len(dataJSON["files"])):
        if dataJSON["files"][i]["name"] in typeOfData:
            for j in range(len(dataJSON["files"][i]["attributes"])):
                if dataJSON["files"][i]["attributes"][j]['name'] == dataName:
                    result = dataJSON["files"][i]["attributes"][j]['values']
                    return result
    raise Exception(f'{dataName} not found in the fort.json file')

def GetIndiceData(dataJSON:dict, dataName:str)->list:
    """Returns the list of data desginated by the name 'dataName' in a fort.JSON
    @Param dataJSON : the imported content of the JSON file
    @Param dataName : the name of the data we want to access (ex : 'SECTNBSE' for the number of watched sections)
    @Return : the list of the data"""

    if dataName not in DicoTypeByData : raise Exception(f'{dataName} not found in the usual list of fort.JSON section name')
    typeOfData = DicoTypeOfData[DicoTypeByData[dataName]]
    for i in range(len(dataJSON["files"])):
        if dataJSON["files"][i]["name"] in typeOfData:
            for j in range(len(dataJSON["files"][i]["attributes"])):
                if dataJSON["files"][i]["attributes"][j]['name'] == dataName:
                    result = dataJSON["files"][i]["attributes"][j]['values']
                    return (i,j)
    raise Exception(f'{dataName} not found in the fort.json file')

def getIndiceElement(dataJSON:dict, sectionName:str)->dict:
    """Gets the indices of the Elemnt liste in the section (groups, TDs, consumption, etc.)
    @Param dataJSON : the imported content of the json file
    @Param sectionName : the name of the section that lists the names of the elements we want
    @Return : a dictionnary with the name of the elements as keys and 
    their indices in the JSON file as value"""

    dictGroup = {}
    groupList = searchForData(dataJSON,sectionName)
    for j in range(len(groupList)):
        dictGroup[groupList[j]] = j
    return dictGroup

def getGroupProdMinAR(group:str,variant:int,dataJSON:dict,dicoVariants:dict)->float:
    """Gets the puiMin_ value used in Metrix
    @Param group : name of the group whose minimum production capacity we want
    @Param variant : number of the variant for which we want this info
    @Param dataJSON : a dictionnary of the data in the fort.json
    @Param dicoVariants : a dictionnary of the data in the VariantSet.csv
    @Return : the minimum production capacity of the group for the specified variant"""

    if "TRPUIMIN" in dicoVariants[variant] and group in dicoVariants[variant]['TRPUIMIN']:
        return Decimal(dicoVariants[variant]['TRPUIMIN'][group])
    
    if -1 in dicoVariants and "TRPUIMIN" in dicoVariants[-1] and group in dicoVariants[-1]['TRPUIMIN']:
        return Decimal(dicoVariants[-1]['TRPUIMIN'][group])
    
    listProdHR = searchForData(dataJSON, "TRPUIMIN")
    puiMinBase = listProdHR[getIndiceElement(dataJSON,"TRNOMGTH")[group]]
    return Decimal(puiMinBase)
    
def getIndiceStartAndEndLine(dataJSON:dict,dictLine:dict,nameLine:str)->tuple:
    tnnorqua = searchForData(dataJSON,"TNNORQUA")[dictLine[nameLine]]
    tnnexqua = searchForData(dataJSON,"TNNEXQUA")[dictLine[nameLine]]
    return((tnnorqua,tnnexqua))

def getMinCostDelestageConsoAR(conso:str,variant_number:int,dataJSON:dict,dicoVariants:dict)->float:
    """Gets the cost of the redispatching of a consumption area
    for the specific variant
    @Param conso : name of the consumption are
    @Param variant_number : number of the variant
    @Param dataJSON : the data of the JSON file, in form of a dictionnary
    @Param dicoVariants : the data of the VariantSet.csv, in form of a dictionnary
    @Return : the cost of the consumption area"""

    indiceConso = getIndiceElement(dataJSON,"TNNOMNOE")[conso]
    if (variant_number in dicoVariants and
        "COUEFFAR" in dicoVariants[variant_number] and
        conso in dicoVariants[variant_number]["COUEFFAR"]):
        return Decimal(dicoVariants[variant_number]["COUEFFAR"][conso])
    elif (-1 in dicoVariants and
        "COUEFFAR" in dicoVariants[variant_number] and
        conso in dicoVariants[variant_number]["COUEFFAR"]):
        return Decimal(dicoVariants[-1]["COUEFFAR"][conso])
    else:
        try:
            listCostDelestage = searchForData(dataJSON, "TNVACOU1")
            costDelestage = Decimal(listCostDelestage[indiceConso])
            return costDelestage
        except:
            return Decimal(13000.0)

def getMinCostDelestageConsoHR(conso:str,variant_number:int,dataJSON:dict,dicoVariants:dict)->float:
    """Gets the cost of the redispatching of a consumption area
    for the specific variant
    @Param conso : name of the consumption are
    @Param variant_number : number of the variant
    @Param dataJSON : the data of the JSON file, in form of a dictionnary
    @Param dicoVariants : the data of the VariantSet.csv, in form of a dictionnary
    @Return : the cost of the consumption area"""

    indiceConso = getIndiceElement(dataJSON,"TNNOMNOE")[conso]
    if (variant_number in dicoVariants and
        "COUEFFHR" in dicoVariants[variant_number] and
        conso in dicoVariants[variant_number]["COUEFFHR"]):
        return Decimal(dicoVariants[variant_number]["COUEFFHR"][conso])
    elif (-1 in dicoVariants and
        "COUEFFHR" in dicoVariants[variant_number] and
        conso in dicoVariants[variant_number]["COUEFFHR"]):
        return Decimal(dicoVariants[-1]["COUEFFHR"][conso])
    else:
        try:
            listCostDelestage = searchForData(dataJSON, "TNVACOU1")
            costDelestage = Decimal(listCostDelestage[indiceConso])
            return costDelestage
        except:
            return Decimal(13000.0)

def getGroupProdMinHR(group:str,variant:int,dataJSON:dict,dicoVariants:dict)->float:
    """Gets the puiMin_ value used in Metrix
    @Param group : name of the group whose minimum production capacity we want
    @Param variant : number of the variant for which we want this info
    @Param dataJSON : a dictionnary of the data in the fort.json
    @Param dicoVariants : a dictionnary of the data in the VariantSet.csv
    @Return : the minimum production capacity of the group for the specified variant"""

    #Dans Metrix, en adequacy, une puissance minimale positive est considérée comme nulle.
    if "TRPUIMIN" in dicoVariants[variant] and group in dicoVariants[variant]['TRPUIMIN']:
        puiMin = Decimal(dicoVariants[variant]['TRPUIMIN'][group])
        if puiMin <= 0.0 : 
            return puiMin
        return Decimal(0.0)
    if -1 in dicoVariants and "TRPUIMIN" in dicoVariants[-1] and group in dicoVariants[-1]['TRPUIMIN']:
        puiMin = Decimal(dicoVariants[-1]['TRPUIMIN'][group])
        if puiMin <= 0.0 : 
            return puiMin
        return Decimal(0.0)
    
    listProdHR = searchForData(dataJSON, "TRPUIMIN")
    puiMinBase = listProdHR[getIndiceElement(dataJSON,"TRNOMGTH")[group]]
    if puiMinBase > 0.0:
        #Dans Metrix, une puissance de production minimale >0
        #est considérée comme nulle
        return Decimal(0.0)
    return Decimal(puiMinBase)

fort48_addition={
    "name" : "fort.48_BIN",
    "attributes" : [{
      "name" : "RAZGROUP",
      "type" : "BOOLEAN",
      "valueCount" : 1,
      "firstIndexMaxValue" : 1,
      "secondIndexMaxValue" : 1,
      "firstValueIndex" : 1,
      "lastValueIndex" : 1,
      "values" : [ "true" ]
    }]
}

RAZGROUP_addition={
      "name" : "RAZGROUP",
      "type" : "BOOLEAN",
      "valueCount" : 1,
      "firstIndexMaxValue" : 1,
      "secondIndexMaxValue" : 1,
      "firstValueIndex" : 1,
      "lastValueIndex" : 1,
      "values" : [ "true" ]
    }


def addRAZGroupBoolean(dataJSON:dict)->None:
    """If the 'RAZGROUP' value isn't in the JSON file or is 
    set to false, we add it or put it to true. Then we save it.
    @Param addressfortJSON : the address of the fort.json"""

    fort48_found = False
    RAZGROUP_found = False
    typeOfData = DicoTypeOfData[DicoTypeByData["RAZGROUP"]]
    for i in range(len(dataJSON["files"])):
        if dataJSON["files"][i]["name"] in typeOfData:
            fort48_found = True
            for j in range(len(dataJSON["files"][i]["attributes"])):
                if dataJSON["files"][i]["attributes"][j]['name'] == "RAZGROUP":
                    RAZGROUP_found = True
                    print("RAZGROUP déjà présent, on le passe à 'True'")
                    dataJSON["files"][i]["attributes"][j]['values'] = [ "true" ]
                    break
            if not RAZGROUP_found :
                dataJSON["files"][i]["attributes"].append(RAZGROUP_addition)
                break
            if RAZGROUP_found : break
    if not fort48_found :
        dataJSON["files"].append(fort48_addition)

fort45_PENA_addition={
    "name" : "fort.45_BIN",
    "attributes" : [{
      "name" : "X",
      "type" : "FLOAT",
      "valueCount" : 1,
      "firstIndexMaxValue" : 1,
      "secondIndexMaxValue" : 1,
      "firstValueIndex" : 1,
      "lastValueIndex" : 1,
      "values" : [ 0.1 ]
    }]
}

PENA_addition={
      "name" : "X",
      "type" : "FLOAT",
      "valueCount" : 1,
      "firstIndexMaxValue" : 1,
      "secondIndexMaxValue" : 1,
      "firstValueIndex" : 1,
      "lastValueIndex" : 1,
      "values" : [ 0.1 ]
    }


def addPENAFloat(dataJSON:dict, value:float, typePENA:str)->None:
    """If the 'HVDC' or 'TD' (designated by typePENA) value isn't in the JSON file, we add it and put it at value. Then we save it.
    @Param addressfortJSON : the address of the fort.json
    @Param value : the value we want to put for 'HVDCPENA' in the fort.json
    @Param typePENA : the type of cost penalty we implement : for TD ('TDPENALI') or HVDC ('HVDCPENA')"""

    fort45_found = False
    PENA_found = False
    typeOfData = DicoTypeOfData[DicoTypeByData[typePENA]]
    #Cette boucle permet de vérifier qu'il n'y a pas déjà la section qu'on veut, et dans un autre type de données (float, Integer)
    # que celle voulue
    for i in range(len(dataJSON["files"])):
        if PENA_found : break
        for j in range(len(dataJSON["files"][i]["attributes"])):
            if typePENA == dataJSON["files"][i]["attributes"][j]['name']:
                fort45_found = True
                PENA_found = True
                break
    #Si on n'a rien trouvé, on cherche et on insère la nouvelle section
    for i in range(len(dataJSON["files"])):
        if (PENA_found):break    
        if dataJSON["files"][i]["name"] in typeOfData:
            fort45_found = True
            dataJSON["files"][i]["attributes"].append(PENA_addition.copy())
            dataJSON["files"][i]["attributes"][len(dataJSON["files"][i]["attributes"]) - 1]['values'] = [ value ]
            dataJSON["files"][i]["attributes"][len(dataJSON["files"][i]["attributes"]) - 1]['name'] = typePENA
            break
    if not fort45_found :
        print("Fort45 pas trouvée")
        dataJSON["files"].append(fort45_PENA_addition.copy())
        dataJSON["files"][len(dataJSON["files"]) - 1]["attributes"][0]["values"] = [ value ]
        dataJSON["files"][len(dataJSON["files"]) - 1]["attributes"][0]["name"] = typePENA