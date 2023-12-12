import json
from sys import argv
import pandas as pd
import os.path
from decimal import *
from pprint import pprint
import extractDataJSON

UndefinedValue = -1e9
precision = 4 #Precision of the epsilon defined below
epsilon = Decimal("{:.{}f}".format(0.1**precision,precision))
rate_of_selection = 0.001


def createDicoFromCsv(address:str)->dict:
    """Creates a dictionnary of the information
    stored in the "VariantSet.csv" 
    @Param address : the address of the VariantSet.csv file
    @Return dico : dictionnary containing all the data of the VariantSet.csv"""

    with open(address) as file:
        dico = {}
        variant = "X"
        variant_int = UndefinedValue
        #List of VariantSet.csv entries that do not contain a duo {Name : Value}
        list_non_dico = ["PRODIN","QUADIN","GROURAND"]
        for line in file:
            decomposed_line = line.split(";")[:-1]
            #If a line of the .csv has less than 3 elements, then it contains no information
            if len(decomposed_line)<=3: continue
            
            number_keys = int(decomposed_line[2])

            #For each variant listed in the .csv,
            #we create a new key in the dictionnary "dico"
            if decomposed_line[0] != variant:
                variant = decomposed_line[0]
                variant_int = int(variant)
                dico[variant_int] = {}

            if decomposed_line[1] in list_non_dico:
                if decomposed_line[1] in dico[variant_int]:
                    dico[variant_int][decomposed_line[1]].extend(decomposed_line[3:3+number_keys])
                else:
                    dico[variant_int][decomposed_line[1]] = (decomposed_line[3:3+number_keys])
            else:
                added_keys = 1
                if decomposed_line[1] not in dico[variant_int]: dico[variant_int][decomposed_line[1]] = {}
                for i in range (3, len(decomposed_line),2):
                    if added_keys > number_keys : break
                    dico[variant_int][decomposed_line[1]][decomposed_line[i]] = Decimal(decomposed_line[i+1])
                    added_keys+=1
    return dico

def createCSVFromDico(dicoVariant:dict, test_folder:str)->None:
    """Creates a .csv file called "VariantSet.csv" 
    at the test_folder location out of the information
    stored in dicoVariant 
    @Param dicoVariant : Dictionnary storing all the information
    we want to put in a VariantSet.csv file
    @Param test_folder : the address where we want to put this new .csv file"""

    if test_folder[-1] == "/":
        end_line = ""
    else:
        end_line = "/"
    addressVariantSet = test_folder + end_line + 'VariantSet.csv'

    text = []
    list_non_dico = ["PRODIN","QUADIN","GROURAND"]
    #List of entries in the fort.json that do not contain a dictionnary
    number_of_variants = 0

    for variant_number in dicoVariant:
    #We check that each variant is calculated (sometimes, some variants are uncalculated)
        if variant_number == -1: continue
        #Read the output_data of the variant on the production
        variant_address = test_folder + end_line + "out_s" + str(variant_number)
        if not os.path.exists(variant_address): continue
        number_of_variants += 1

    text.append("NT;" + str(number_of_variants) + ";" + "\n")
    
    for variant in dicoVariant:
    #for each variant, we write its content in  .csv format and add it to the "text" list
        if variant == 0:
            text.append("0;" + "\n")
        for infoType in dicoVariant[variant]:
            line = str(variant)+";"+infoType+";"+str(len(dicoVariant[variant][infoType]))+";"
            if infoType in list_non_dico:
                for list_element in dicoVariant[variant][infoType]:
                    line += list_element + ";"
            else: 
                for key in dicoVariant[variant][infoType]:
                    value = dicoVariant[variant][infoType][key]
                    string_value = str(value) if str(value)[-2:] != '.0' else str(value)[:-2]
                    line += str(key) + ";" + string_value + ";"
            line += "\n"
            text.append(line)
    with open(addressVariantSet, "w") as file:
        file.writelines(text)


def getGroupCost(dicoVariants:dict, group:str, variant:int, typeOfCost:str)->tuple:
    """Gets the increase or decrease cost of production in adequacy phase
    for a group in a specific variant
    and the number of the variant where it is defined
    (variant or former variants or -1 or None)
    @Param dicoVariants : the dictionnary storing all the informations
    of the variants
    @Param group : the name of the group whose Adequacy cost we want
    @Param variant : the variant for which we want the cost
    @Param TypeOfCost : the type of cost we want : CTORDR, COUBHR, COUHAR or COUBAR
    @Return (cost, numVariant) : the value of the wanted type of cost as 
    well as the variant where it is defined"""
    
    listDicoKeys = list(dicoVariants.keys())
    variant_index = listDicoKeys.index(variant)
    numVariant = UndefinedValue
    cost = 0.0

    for i in range(variant_index,-1,-1):
        variant_number = listDicoKeys[i]
        if numVariant == UndefinedValue:
            if typeOfCost in dicoVariants[variant_number] and group in dicoVariants[variant_number][typeOfCost]:
                cost = dicoVariants[variant_number][typeOfCost][group]
                numVariant = variant_number
    return (cost, numVariant)

def read_RX(address:str,category:str)->pd.DataFrame:
    """Returns a Dataframe of the information stored
    in the 'RX' (or 'CX') section of the out file designated
    by the address, wth RX designated by the parameter 'category'"""

    with open(address) as variant_result_file:
        listed_text = []
        for line in variant_result_file:
            if line.startswith(f"{category} "):
                listed_text.append(line[:-1]) if line[-1] == '\n' else listed_text.append(line)
    if listed_text == []:
        #If there are no RX ligns, we return an empty dataframe
        return pd.DataFrame()
    df = [n.split(';') for n in listed_text]
    if len(df) <= 1:
        #If we only have the header of the RX part, we return en empty dataframe
        #having this header
        df = pd.DataFrame(columns=df[0])
    else:
        #we return the complete RX data in the dataframe
        df = pd.DataFrame(df[1:], columns=df[0][0:len(df[1])])
    return(df)

fort44_addition={
    "name" : "fort.44_BIN",
    "attributes" : [{
      "name" : "ADEQUAOF",
      "type" : "INTEGER",
      "valueCount" : 1,
      "firstIndexMaxValue" : 1,
      "secondIndexMaxValue" : 1,
      "firstValueIndex" : 1,
      "lastValueIndex" : 1,
      "values" : [ 0 ]
    }]
}

ADEQUAOF_addition={
      "name" : "ADEQUAOF",
      "type" : "INTEGER",
      "valueCount" : 1,
      "firstIndexMaxValue" : 1,
      "secondIndexMaxValue" : 1,
      "firstValueIndex" : 1,
      "lastValueIndex" : 1,
      "values" : [ 0 ]
    }


def getAdequacyCostOffsetValue(addressfortJSON:str)->tuple:
    """Search for the ADEQUAOF value in a fort.json file.
    @Param addressfortJSON : address of the fort.json file
    @Return (adequacyCostOffset, sectionCoordOfADEQUAOF) : the value of the adequacy cost offset 
    and the coordinates of the ADEQUAOF section in the fort.JSON"""

    adequacyCostOffset = 0
    sectionCoordOfADEQUAOF = [UndefinedValue,UndefinedValue]

    #Get the value of adequacyCostOffset from the fort.json
    with open(addressfortJSON) as file:
        fortJSON = json.load(file)

    List_sections_number = []
    for i in range(len(fortJSON)):
        if fortJSON["files"][i]['name'] == "fort.44_BIN" or fortJSON["files"][i]['name'] == 'IntegerFile': 
            sectionCoordOfADEQUAOF[0] = i
            List_sections_number.append(i)
        if fortJSON["files"][i]['name'] == "fort.45_BIN" or fortJSON["files"][i]['name'] == 'DecimalFile': 
            List_sections_number.append(i)
    for j in List_sections_number:
        for k in range(len(fortJSON['files'][j]['attributes'])):
            if fortJSON['files'][j]['attributes'][k]['name'] == "ADEQUAOF":
                sectionCoordOfADEQUAOF = [j,k]
                adequacyCostOffset = fortJSON['files'][j]['attributes'][k]['values'][0]
    return(adequacyCostOffset, sectionCoordOfADEQUAOF)


def getMinCostGroupsAndNumberInAdequacy(addressVariantSet:str, addressFortJSON:str, adequacyCostOffsetInitial:float, noiseCost:float)->float:
    """Gets the maximal number of groups modified for each variants
    @Param addressVariantSet : address of the VariantSet.csv
    @Param addressFortJSON : address of the fort.json
    @Param adequacyCostOffsetInitial : initial value of the adequacy offset 
    @Param noiseCost : value of the noiseCost
    @Return adequacyCostOffset : the new value of adequacyCostOffset, adapted so that 
    we can increment the costs of the modified groups by epsilon between 0 and the minimal group cost."""
    
    dicoVariantSet = createDicoFromCsv(addressVariantSet)
    listVariantsNumber = list(dicoVariantSet.keys())
    adequacyCostOffset = adequacyCostOffsetInitial
    
    for variantNumber in listVariantsNumber:
        if variantNumber == -1 : continue
        minimalCost = {'COUBHR' : abs(UndefinedValue), "CTORDR": abs(UndefinedValue)}
        maxNumberOfGroupsInTNR = {'COUBHR' : 0.0, "CTORDR":0.0}
        groupAndCostType = []
        addressVariantOut = addressFortJSON[:-9] + "out_s" + str(variantNumber)
        if not os.path.exists(addressVariantOut):
            continue
        df_out = read_RX(addressVariantOut, "R2")
        for idx in df_out.index:
            if df_out['DELTA_P_HR'][idx] != "":
                costT = 'CTORDR' if Decimal(df_out['DELTA_P_HR'][idx]) > 0.0 else 'COUBHR'
                maxNumberOfGroupsInTNR[costT] += 1
                groupAndCostType.append((df_out['GROUPE'][idx],costT))

        for (group,costType) in groupAndCostType:
        #For each double in groupAndCostType, we check the cost of group
        # for the appropriate cost-type : it can be define in every variant
        #between the current one and -1. If it i not, its cost is 0
        #If it is inferior to our minimum, it becomes our new minimum.
            if costType in dicoVariantSet[variantNumber] and group in dicoVariantSet[variantNumber][costType]:
                if dicoVariantSet[variantNumber][costType][group] < minimalCost[costType]:
                    minimalCost[costType] = dicoVariantSet[variantNumber][costType][group]
            elif -1 in dicoVariantSet and costType in dicoVariantSet[-1] and group in dicoVariantSet[-1][costType]:
                if dicoVariantSet[-1][costType][group] < minimalCost[costType]:
                    minimalCost[costType] = dicoVariantSet[-1][costType][group]
            else: minimalCost[costType] = 0.0

        for costType in maxNumberOfGroupsInTNR:
            if maxNumberOfGroupsInTNR[costType] == 0 : continue

            #If the minimal group cost used by Metrix divided by the number of modified groups is inferior to epsilon,
            #we adapt the adequacyCostOffset so that it isn't the case anymore
            if Decimal((Decimal(minimalCost[costType]) + Decimal(adequacyCostOffset) + Decimal(noiseCost)))/Decimal(maxNumberOfGroupsInTNR[costType]) < epsilon :
                adequacyCostOffset = int(epsilon*maxNumberOfGroupsInTNR[costType] - minimalCost[costType]) + 1
    
    return adequacyCostOffset


def addAdequacyCostInFortJSON(addressfortJSON : str,sectionCoordOfADEQUAOF : list, adequacyCostOffset : float) -> None:
    """Changes the value of the Adequacy Cost Offset in the fort.json file
    @Param addressfortJSON : the address of the fort.JSON file
    @Param sectionCoordOfADEQUAOF : the list containing the indices of the Float section
    in the file and of the ADEQUAOF section in it
    @Param float adequacyCostOffset : the new value of the adequacty Cost Offset to implement
    """

    with open(addressfortJSON) as file:
            fortJSON = json.load(file)

    if sectionCoordOfADEQUAOF == [UndefinedValue, UndefinedValue]:
        fortJSON['files'].append(fort44_addition)
        fortJSON['files'][-1]['attributes'][0]['values'][0] = adequacyCostOffset
    elif sectionCoordOfADEQUAOF[0] != UndefinedValue:
        fortJSON['files'][sectionCoordOfADEQUAOF[0]]['attributes'].append(ADEQUAOF_addition)
        fortJSON['files'][sectionCoordOfADEQUAOF[0]]['attributes'][-1]['values'][0] = adequacyCostOffset
    else:
        fortJSON['files'][sectionCoordOfADEQUAOF[0]]['attributes'][sectionCoordOfADEQUAOF[1]]['values'] = adequacyCostOffset

    with open(addressfortJSON, "w") as file:
        json.dump(fortJSON,file, indent=1)

def typeOfCostIdentical(typeOfCost:str, value:float)->bool:
    """Checks if a value is of the corresponding type : 
    CTORDR or COUHAR for positive values, else COUBHR or COUBAR 
    @Param typeOfCost : the type of cost : CTORDR, COUHAR, COUBAR or COUBHR
    @Param value : the cost to compare with the type of cost
    @Return : a boolean"""
    if value > 0.0 and (typeOfCost == 'CTORDR' or typeOfCost == 'COUHAR'):
        return True
    if value < 0.0 and (typeOfCost == "COUBHR" or typeOfCost == 'COUBAR'):
        return True
    return False 

def ChangeHRGroupConsoCostsByEpsilon(test_folder:str, dicoVariants:dict,dataJSON:dict):
    """Subtracts an epsilon to the HR cost of the groups, so as to favor the groups that are used in the adequacy phase of the solution,
    with priority to the groups that used to their maximum capacity, and then to the ones with the biggest power modification. 
    We do the same for the deleted consumption.
    @Param test_folder : address of the folder containing the out files, the VariantSet.csv and fort.json
    @Param dicoVariants : dict containing all the data of the VariantSet.csv
    @Param dataJSON : dict containing all the data of the fort.json
    @Return dicoVariants : modified dict in which the HR costs of the groups are modified by an epsilon"""
    
    if test_folder[-1] == "/":
        end_line = ""
    else:
        end_line = "/"

    usedGroups = {'CTORDR' :{}, 'COUBHR' :{}} # Stores the groups whose costs we were redefined using epsilon in former variants
    # Each dictionnary will contain name of the group -> Initial cost

    for variant_number in dicoVariants:
        print('Traitement HR : Variante ',variant_number)
        
        #We import the VariantSet.csv and check that it has any adequacy going on
        variant_address = test_folder + end_line + "out_s" + str(variant_number)

        #We check that the variant file does exist (for instance, variant -1 never does)
        if not os.path.exists(variant_address):
            print("Le fichier out_s",variant_number," n'existe pas, on l'ignore")
            continue

        #We check that the simulation worked correctly and has info to show
        df_variant_C1 = read_RX(variant_address, "C1")
        if not df_variant_C1.empty:
            if df_variant_C1["CODE"][0] != "0":
                print("Le fichier de la variante ",variant_number," est vide. On passe aux variantes suivantes.")
                continue
        
        df_variantR2 = read_RX(variant_address, "R2")
        
        # We store the R2 & R1 sections of the out file ot his variant.
        # We keep only the ligns that present a non-null adequacy phase.
        if not df_variantR2.empty:
            df_variantR2 = df_variantR2[df_variantR2["DELTA_P_HR"] != '']

        df_variantR1 = read_RX(variant_address,"R1")
        df_variantR1 = df_variantR1[df_variantR1['DF HR'] != '']
        if df_variantR1.empty and df_variantR2.empty :
            continue

        used_groups_CTORDR = [] #stores the name of the groups who were used to increase production in this variant
        used_groups_COUBAR = [] #stores the name of the groups who were used to decrease production in this variant
        typeOfGroup = {'CTORDR' : used_groups_CTORDR, 'COUBHR' : used_groups_COUBAR}
                        
        # We list the groups that are used in this variant : they will be 
        # favored by decreasing their cost of an epsilon
        if not df_variantR2.empty:
            for idx in df_variantR2.index:
                group = df_variantR2['GROUPE'][idx]
                #We check if the current group has its power pushed to Pmin or Pmax.
                #To do that, as the production displayed in the out files is precise to
                #0.1, we compare it to that instead of 0
                if Decimal(df_variantR2['DELTA_P_HR'][idx]) > 0.0:
                    #If the group is used to increase production
                    maxedProd = (abs(Decimal(df_variantR2['PDISPO'][idx]) - Decimal(df_variantR2['DELTA_PIMP'][idx]) - Decimal(df_variantR2['DELTA_P_HR'][idx])) <= Decimal(rate_of_selection))
                    used_groups_CTORDR.append((group, Decimal(df_variantR2['DELTA_P_HR'][idx]), maxedProd))
                    if group not in usedGroups['CTORDR']:
                        (cost, numVariant) = getGroupCost(dicoVariants, group, variant_number, "CTORDR")
                        if numVariant == -1 or numVariant == UndefinedValue:
                            usedGroups['CTORDR'][group] = cost

                else:
                    #We have to find the minimum production of the group. As it is not displayed in the 
                    #output file, we have to look for it in the JSON file
                    prodMin = extractDataJSON.getGroupProdMinHR(group,variant_number,dataJSON,dicoVariants)
                    maxedProd = (abs(Decimal(df_variantR2['DELTA_PIMP'][idx]) + Decimal(df_variantR2['DELTA_P_HR'][idx]) - prodMin) <= Decimal(rate_of_selection))
                    used_groups_COUBAR.append((group, abs(Decimal(df_variantR2['DELTA_P_HR'][idx])), maxedProd))
                    if group not in usedGroups['COUBHR']:
                        (cost, numVariant) = getGroupCost(dicoVariants, group, variant_number, "COUBHR")
                        if numVariant == -1 or numVariant == UndefinedValue:
                            usedGroups['COUBHR'][group] = cost
        
        if not df_variantR1.empty:
            for idx in df_variantR1.index:
                conso = df_variantR1['CONSO'][idx]
                currentConso = Decimal(df_variantR1['VALEUR'][idx])
                changedConso = Decimal(df_variantR1['DF HR'][idx])
                erasedConso = (abs(changedConso - currentConso) <= Decimal(rate_of_selection))
                used_groups_COUBAR.append((conso, changedConso, erasedConso))
        
        # We sort the values by increasing production or consumption and by whether
        # the group reached its Pmin or Pmax.
        used_groups_CTORDR.sort(key=lambda item: (item[2],item[1]))
        used_groups_COUBAR.sort(key=lambda item: (item[2],item[1]))

        for typeOfElement in typeOfGroup:
            #We substract added_cost to the existing cost of the groups ; added_cost's value increments
            #if the groups have a different power, we add epsilon to added_cost.
            #If the original cost of a group is negative, we change it to 0,
            #and then aply the epsilonesque modification
            added_cost = Decimal(0.0)
            former_power = 0.0
            #We add the noise cost to the conso ; it cannot be found in any file, 
            #it is embedded in the Metrix code
            
            for (used_group,power, bool) in typeOfGroup[typeOfElement]:
                if used_group in df_variantR1['CONSO'].values:
                    typeOfCost = "COUEFFHR"
                    existing_cost = extractDataJSON.getMinCostDelestageConsoHR(used_group,variant_number,dataJSON,dicoVariants)
                else:
                    typeOfCost = typeOfElement
                    existing_cost = Decimal(0.0)
                if former_power != power:
                    added_cost += epsilon
                    former_power = power

                if (-1 in dicoVariants and typeOfCost in dicoVariants[-1] 
                    and used_group in dicoVariants[-1][typeOfCost] and 
                    dicoVariants[-1][typeOfCost][used_group] >= 0.0
                    and typeOfCost != "COUEFFHR"):
                    existing_cost = dicoVariants[-1][typeOfCost][used_group]
                
                if variant_number not in dicoVariants:
                    dicoVariants[variant_number] = {typeOfCost:{used_group : Decimal("{:.{}f}".format(existing_cost - added_cost,precision))}}
                elif typeOfCost not in dicoVariants[variant_number]:
                    dicoVariants[variant_number][typeOfCost] = {used_group : Decimal("{:.{}f}".format(existing_cost - added_cost,precision))}
                elif used_group not in dicoVariants[variant_number][typeOfCost]:
                    dicoVariants[variant_number][typeOfCost][used_group] = Decimal("{:.{}f}".format(existing_cost - added_cost,precision))
                else:
                    if dicoVariants[variant_number][typeOfCost][used_group] >= 0.0:
                        dicoVariants[variant_number][typeOfCost][used_group] -= Decimal("{:.{}f}".format(added_cost,precision))
                    else:
                        #We don't add additionnal cost here because having a consumption area paying to stop consuming is illogical
                        #And will make the study bug
                        dicoVariants[variant_number][typeOfCost][used_group] = -Decimal("{:.{}f}".format(added_cost,precision))
        
        # We redefine the costs of the groups that were used before but not in this variant

        # If some groups were used to increase (or decrease) production in former variants, we have to
        # redefine their costs in the next variant. Unless this next variant doesn't need
        # to increase (or decrease) production : then we don't redefine the costs of those groups used before.
        # That is what we check here.
    for typeOfCost in usedGroups:
        for group in usedGroups[typeOfCost]:
            #If a group has a cost in this list, then its cost isn't defined in every variant : we have to 
            #put the original cost in every variant that we haven't modified
            for variant_number in dicoVariants:
                if variant_number == -1 : continue
                if typeOfCost not in dicoVariants[variant_number]:
                    dicoVariants[variant_number][typeOfCost] = {group : usedGroups[typeOfCost][group]}
                elif group not in dicoVariants[variant_number][typeOfCost]:
                    dicoVariants[variant_number][typeOfCost][group] = usedGroups[typeOfCost][group]
                else:
                    continue

    return dicoVariants

def ChangeARGroupConsoCostsByEpsilon(test_folder:str, dicoVariants:dict,dataJSON:dict):
    """Subtracts an epsilon to the AR cost of the groups, so as to favor the groups that are used in the redispatching phase of the solution,
    with priority to the groups that used to their maximum capacity, and then to the ones with the biggest power modification.
    Does the same with the consumption. Also we reduce by an epsilon the threshold of all lines appearing in the R4 section
    @Param test_folder : address of the folder containing the out files, the VariantSet.csv and fort.json
    @Param dicoVariants : dict containing all the data of the VariantSet.csv
    @Param dataJSON : dict containing all the data of the fort.json
    @Return dicoVariants : modified dict in which the HR costs of the groups are modified by an epsilon"""
    
    if test_folder[-1] == "/":
        end_line = ""
    else:
        end_line = "/"

    usedGroups = {'COUHAR' :{}, 'COUBAR' :{}} # Stores the groups whose costs were redefined using epsilon in former variants
    # Each dictionnary will contain name of the group -> Initial cost

    for variant_number in dicoVariants:
    # for variant_number in range(-1,7):
        print('Traitement AR préventif : Variante ',variant_number)
        #We import the VariantSet.csv and check that it has any redispatching going on
        variant_address = test_folder + end_line + "out_s" + str(variant_number)
        if not os.path.exists(variant_address):
            continue

        #We check that the simulation worked correctly and has info to show
        df_variant_C1 = read_RX(variant_address, "C1")
        if not df_variant_C1.empty:
            if df_variant_C1["CODE"][0] != "0":
                print("Le fichier de la variante ",variant_number," est vide. On passe aux variantes suivantes.")
                continue

        df_variantR2 = read_RX(variant_address, "R2")
        
        # We store the R2 section of the out file ot his variant.
        # We keep only the ligns that present a non-null adequacy phase.
        if not df_variantR2.empty:
            df_variantR2 = df_variantR2[df_variantR2["DELTA_P_AR"] != '']

        df_variantR1 = read_RX(variant_address, "R1")
        if not df_variantR1.empty:
            df_variantR1 = df_variantR1[df_variantR1['DF AR'] != '']

        used_groups_COUHAR = [] #stores the name of the groups who were used to increase production in this variant
        used_groups_COUBAR = [] #stores the name of the groups who were used to decrease production in this variant
        typeOfGroup = {'COUHAR' : used_groups_COUHAR, 'COUBAR' : used_groups_COUBAR}

        # We list the groups that are used in this variant : they will be 
        # favored by decreasing their cost of an epsilon
        if not df_variantR2.empty:
            for idx in df_variantR2.index:
                group = df_variantR2['GROUPE'][idx]
                #We check if the current group has its power pushed to Pmin or Pmax.
                #To do that, as the production displayed in the out files is precise to
                #0.1, we compare it to that instead of 0
                if Decimal(df_variantR2['DELTA_P_AR'][idx]) > 0.0:
                    #If the group is used to increase production
                    maxedProd = (abs(Decimal(df_variantR2['PDISPO'][idx]) - Decimal(df_variantR2['DELTA_PIMP'][idx]) - Decimal(df_variantR2['DELTA_P_AR'][idx])) <= Decimal(rate_of_selection))
                    used_groups_COUHAR.append((group, Decimal(df_variantR2['DELTA_P_AR'][idx]), maxedProd))
                    if group not in usedGroups['COUHAR']:
                        (cost, numVariant) = getGroupCost(dicoVariants, group, variant_number, "COUHAR")
                        if numVariant == -1 or numVariant == UndefinedValue:
                            usedGroups['COUHAR'][group] = cost

                else:
                    #We have to find the minimum production of the group. As it is not displayed in the 
                    #output file, we have to look for it in the JSON file
                    prodMin = extractDataJSON.getGroupProdMinAR(group,variant_number,dataJSON,dicoVariants)
                    maxedProd = (abs(Decimal(df_variantR2['DELTA_PIMP'][idx]) + Decimal(df_variantR2['DELTA_P_AR'][idx]) - prodMin) <= Decimal(rate_of_selection))
                    used_groups_COUBAR.append((group, abs(Decimal(df_variantR2['DELTA_P_AR'][idx])), maxedProd))
                    if group not in usedGroups['COUBAR']:
                        (cost, numVariant) = getGroupCost(dicoVariants, group, variant_number, "COUBAR")
                        if numVariant == -1 or numVariant == UndefinedValue:
                            usedGroups['COUBAR'][group] = cost
        
        if not df_variantR1.empty:
            for idx in df_variantR1.index:
                conso = df_variantR1['CONSO'][idx]
                currentConso = Decimal(df_variantR1['VALEUR'][idx])
                changedConso = Decimal(df_variantR1['DF AR'][idx])
                erasedConso = (abs(changedConso - currentConso) <= Decimal(rate_of_selection))
                used_groups_COUBAR.append((conso, changedConso, erasedConso))
        
        # We sort the values by increasing production or consumption and by whether
        # the group reached its Pmin or Pmax.
        used_groups_COUHAR.sort(key=lambda item: (item[2],item[1]))
        used_groups_COUBAR.sort(key=lambda item: (item[2],item[1]))

        for typeOfElement in typeOfGroup:
            #We substract added_cost to the existing cost of the groups ; added_cost's value increments
            #if the groups have a different power, we add epsilon to added_cost.
            #If the original cost of a group is negative, we change it to 0,
            #and then aply the epsilonesque modification
            added_cost = Decimal(0.0)
            former_power = 0.0
            #We add the noise cost to the conso ; it cannot be found in any file, 
            #it is embedded in the Metrix code
            
            for (used_group,power, bool) in typeOfGroup[typeOfElement]:
                if used_group in df_variantR1['CONSO'].values:
                    typeOfCost = "COUEFFAR"
                    existing_cost = extractDataJSON.getMinCostDelestageConsoAR(used_group,variant_number,dataJSON,dicoVariants)
                else:
                    typeOfCost = typeOfElement
                    existing_cost = Decimal(0.0)
                if former_power != power:
                    added_cost += epsilon
                    former_power = power

                if (-1 in dicoVariants and typeOfCost in dicoVariants[-1] 
                    and used_group in dicoVariants[-1][typeOfCost] and 
                    dicoVariants[-1][typeOfCost][used_group] >= 0.0
                    and typeOfCost != "COUEFFAR"):
                    existing_cost = dicoVariants[-1][typeOfCost][used_group]
                
                if variant_number not in dicoVariants:
                    dicoVariants[variant_number] = {typeOfCost:{used_group : Decimal("{:.{}f}".format(existing_cost - added_cost,precision))}}
                elif typeOfCost not in dicoVariants[variant_number]:
                    dicoVariants[variant_number][typeOfCost] = {used_group : Decimal("{:.{}f}".format(existing_cost - added_cost,precision))}
                elif used_group not in dicoVariants[variant_number][typeOfCost]:
                    dicoVariants[variant_number][typeOfCost][used_group] = Decimal("{:.{}f}".format(existing_cost - added_cost,precision))
                else:
                    if dicoVariants[variant_number][typeOfCost][used_group] >= 0.0:
                        dicoVariants[variant_number][typeOfCost][used_group] -= Decimal("{:.{}f}".format(added_cost,precision))
                    else:
                        #We don't add additionnal cost here because having a consumption area paying to stop consuming is illogical
                        #And will make the study bug
                        dicoVariants[variant_number][typeOfCost][used_group] = -Decimal("{:.{}f}".format(added_cost,precision))
        
        # We redefine the costs of the groups that were used before but not in this variant

        # If some groups were used to increase (or decrease) production in former variants, we have to
        # redefine their costs in the next variant. Unless this next variant doesn't need
        # to increase (or decrease) production : then we don't redefine the costs of those groups used before.
        # That is what we check here.
    for typeOfCost in usedGroups:
        for group in usedGroups[typeOfCost]:
            #If a group has a cost in this list, then its cost isn't defined in every variant : we have to 
            #put the original cost in every variant that we haven't modified
            for variant_number in dicoVariants:
                if variant_number == -1 : continue
                if typeOfCost not in dicoVariants[variant_number]:
                    dicoVariants[variant_number][typeOfCost] = {group : usedGroups[typeOfCost][group]}
                elif group not in dicoVariants[variant_number][typeOfCost]:
                    dicoVariants[variant_number][typeOfCost][group] = usedGroups[typeOfCost][group]
                else:
                    continue

    return dicoVariants

def changeARTDHVDCCostsByEpsilon(test_folder:str, dicoVariants:dict,dataJSON:dict):
    """Subtracts an epsilon to the AR preventive costs of the TD and HVDC, so as to favor the actions that are used in the preventive phase of the solution,
    with priority to the groups that used to their maximum capacity, and then to the ones with the biggest power modification.
    @Param test_folder : address of the folder containing the out files, the VariantSet.csv and fort.json
    @Param dicoVariants : dict containing all the data of the VariantSet.csv
    @Param dataJSON : dict containing all the data of the fort.json
    @Return dicoVariants : modified dict in which the AR costs of the TDs and HVDCs are modified by an epsilon"""
    
    if test_folder[-1] == "/":
        end_line = ""
    else:
        end_line = "/"

    for variant_number in dicoVariants:
    # for variant_number in range(-1,7):
        print('Traitement TD/HVDC préventif : Variante ',variant_number)
        #We import the VariantSet.csv and check that it has any redispatching going on
        variant_address = test_folder + end_line + "out_s" + str(variant_number)
        if not os.path.exists(variant_address):
            continue

        #We check that the simulation worked correctly and has info to show
        df_variant_C1 = read_RX(variant_address, "C1")
        if not df_variant_C1.empty:
            if df_variant_C1["CODE"][0] != "0":
                print("Le fichier de la variante ",variant_number," est vide. On passe aux variantes suivantes.")
                continue
    
        #FOR THE HVDC : 
        df_variant_R6 = read_RX(variant_address, "R6")
        used_HVDC = []
        if not df_variant_R6.empty:
            
            dicoHVDCNames = extractDataJSON.getIndiceElement(dataJSON, "DCNOMQUA")
            listHVDCPower = extractDataJSON.searchForData(dataJSON, "DCIMPPUI")
            listMaxHVDCPower = extractDataJSON.searchForData(dataJSON, "DCMAXPUI")
            listMinHVDCPower = extractDataJSON.searchForData(dataJSON, "DCMINPUI")
            for idx in df_variant_R6.index:
                HVDCName = df_variant_R6["NOM"][idx]
                actualPower = Decimal(df_variant_R6["TRANSIT"][idx])
                initialPower = Decimal(listHVDCPower[dicoHVDCNames[HVDCName]])
                maxPower = Decimal(listMaxHVDCPower[dicoHVDCNames[HVDCName]])
                minPower = Decimal(listMinHVDCPower[dicoHVDCNames[HVDCName]])
                if variant_number in dicoVariants and "DCIMPPUI" in dicoVariants[variant_number] and HVDCName in dicoVariants[variant_number]["DCIMPPUI"]:
                    initialPower = Decimal(dicoVariants[variant_number]["DCIMPPUI"][HVDCName])
                if variant_number in dicoVariants and "DCMAXPUI" in dicoVariants[variant_number] and HVDCName in dicoVariants[variant_number]["DCMAXPUI"]:
                    maxPower = Decimal(dicoVariants[variant_number]["DCMAXPUI"][HVDCName])
                if variant_number in dicoVariants and "DCMINPUI" in dicoVariants[variant_number] and HVDCName in dicoVariants[variant_number]["DCMINPUI"]:
                    minPower = Decimal(dicoVariants[variant_number]["DCMINPUI"][HVDCName])
                
                HVDCVariation = abs(initialPower - actualPower)
                maxedHVDC = True if (actualPower == maxPower or actualPower == minPower) else False
                used_HVDC.append((HVDCName, HVDCVariation, maxedHVDC))
            used_HVDC.sort(key=lambda item: (item[2],item[1]))
        
        HVDCCost = 0
        if used_HVDC:
            try:
                HVDCCost = extractDataJSON.searchForData(dataJSON,'HVDCPENA')[0]
            except:
                HVDCCost = 0.1
        added_cost = 0.0
        former_HVDC_diff = 0.0
        for HVDC in used_HVDC:
            if former_HVDC_diff != HVDC[1]:
                former_HVDC_diff = HVDC[1]
                added_cost += float(epsilon)
            if variant_number not in dicoVariants:
                dicoVariants[variant_number] = {"COUTLCC":{HVDC[0] : Decimal("{:.{}f}".format(HVDCCost - added_cost,precision))}}
            elif "COUTLCC" not in dicoVariants[variant_number]:
                dicoVariants[variant_number]["COUTLCC"] = {HVDC[0] : Decimal("{:.{}f}".format(HVDCCost - added_cost,precision))}
            elif HVDC[0] not in dicoVariants[variant_number]["COUTLCC"]:
                dicoVariants[variant_number]["COUTLCC"][HVDC[0]] = Decimal("{:.{}f}".format(HVDCCost - added_cost,precision))
            else:
                raise Exception(f'{HVDC[0]} is already written under the COUTLCC section in the VariantSet.csv')
        
        #FOR THE TD :
        df_variant_R5 = read_RX(variant_address, "R5")
        used_TD = []
        if not df_variant_R5.empty:
            
            listQuadNames = extractDataJSON.searchForData(dataJSON, "CQNOMQUA")
            listTDNums = extractDataJSON.searchForData(dataJSON, "DTTRDEQU")
            listInitialDephasage = extractDataJSON.searchForData(dataJSON, "DTVALDEP")
            listMaxDephasage = extractDataJSON.searchForData(dataJSON, "DTVALSUP")
            listMinDephasage = extractDataJSON.searchForData(dataJSON, "DTVALINF")
            
            #Getting and sorting the use of TDs
            for idx in df_variant_R5.index:
                
                quadName = df_variant_R5["TD"][idx]
                quadIndice = listQuadNames.index(quadName)
                TDIndice = listTDNums.index(quadIndice + 1) #it seems the JSON files' list index starts with 1
                actualDephasage = Decimal(df_variant_R5["CONSIGNE"][idx])
                initialDephasage = Decimal(listInitialDephasage[TDIndice])
                maxDephasage = listMaxDephasage[TDIndice]
                minDephasage = listMinDephasage[TDIndice]
                if variant_number in dicoVariants and "DTVALDEP" in dicoVariants[variant_number] and quadName in dicoVariants[variant_number]["DTVALDEP"]:
                    initialDephasage = Decimal(dicoVariants[variant_number]["DTVALDEP"][quadName])
                if variant_number in dicoVariants and "DTVALSUP" in dicoVariants[variant_number] and quadName in dicoVariants[variant_number]["DTVALSUP"]:
                    maxDephasage = Decimal(dicoVariants[variant_number]["DTVALSUP"][quadName])
                if variant_number in dicoVariants and "DTVALINF" in dicoVariants[variant_number] and quadName in dicoVariants[variant_number]["DTVALINF"]:
                    minDephasage = Decimal(dicoVariants[variant_number]["DTVALINF"][quadName])
                maxedTD = True if (actualDephasage == maxDephasage or actualDephasage == minDephasage) else False
                dephasageVariation = abs(actualDephasage - initialDephasage)
                used_TD.append((quadName, dephasageVariation, maxedTD))
            
            used_TD.sort(key=lambda item: (item[2], item[1]))

        #Writing the new costs int the VariantSet.csv
        TDCost = 0
        if used_TD:
            try:
                TDCost = extractDataJSON.searchForData(dataJSON,'TDPENALI')[0]
            except:
                TDCost = 0.01
        added_cost = 0.0
        former_TD_diff = 0.0
        for TD in used_TD:
            if former_TD_diff != TD[1]:
                added_cost += float(epsilon)
                former_TD_diff = TD[1]
            if variant_number not in dicoVariants:
                dicoVariants[variant_number] = {"COUTTD":{TD[0] : Decimal("{:.{}f}".format(TDCost - TDCost - added_cost,precision))}}
            elif "COUTTD" not in dicoVariants[variant_number]:
                dicoVariants[variant_number]["COUTTD"] = {TD[0] : Decimal("{:.{}f}".format(TDCost - added_cost,precision))}
            elif TD[0] not in dicoVariants[variant_number]["COUTTD"]:
                dicoVariants[variant_number]["COUTTD"][TD[0]] = Decimal("{:.{}f}".format(TDCost - added_cost,precision))
            else:
                raise Exception(f'{TD[0]} is already written under the COUTTD section in the VariantSet.csv')

    return dicoVariants

def result(address:str)->dict:
    """Executes the necesary steps to launch ChangeGroupCostByEpsilon
    @Param address : address of the VariantSet.csv and fort.json and out files
    @Return : the new content of the VariantSet.csv, in form of a dictionnary"""
    
    test_folder = address
    if test_folder[-1] == "/":
        end_line = ""
    else:
        end_line = "/"
    
    fort_address = test_folder + end_line + "fort.json"
    variantset_address = test_folder + end_line + "VariantSet.csv"
    
    if not os.path.exists(fort_address):
        raise Exception("Pas de fichier fort.json trouvé")
    if not os.path.exists(variantset_address):
        raise Exception("Pas de fichier VariantSet.csv trouvé")
    
    #Importing the files and creating the data
    dicoVariants = createDicoFromCsv(variantset_address)

    with open(fort_address) as fort_file:
        fort_dict = json.load(fort_file)
    
    dicoVariants = ChangeHRGroupConsoCostsByEpsilon(test_folder, dicoVariants, fort_dict)
    dicoVariants = ChangeARGroupConsoCostsByEpsilon(test_folder, dicoVariants, fort_dict)
    result = changeARTDHVDCCostsByEpsilon(test_folder, dicoVariants, fort_dict)

    return result

def main(argv):
    #ATTENTON! 
    #Pour marcher correctement, les fichiers d'infos de base et de variantes
    #doivent se nommer "fort.json" et "VariantSet.csv". Les fichiers de sortie
    #doivent se nommer "out_sX" avec X le numéro de la variante.
    #Tous ce fichiers qu'on vient de citer doivent se trouver dans le même dossier.
    addressFortJSON = argv[1]
    testAddress = addressFortJSON[:-9]
    #We find if adeqCost is defined and its value
    (adeqCost,sectionCoordOfADEQUAOF) = getAdequacyCostOffsetValue(addressFortJSON)
    addressVariantSet = addressFortJSON[:-9] + "VariantSet.csv"
    print("TNR ",testAddress)

    #We check if the value of adeqCOst is enough : if not, we change it)
    newAdeqCost = getMinCostGroupsAndNumberInAdequacy(addressVariantSet, addressFortJSON, adeqCost, 0.5)
    if adeqCost != newAdeqCost : 
        print("Modification de l'AdequacyCostOffset : Ancienne valeur = ",adeqCost,"; Nouvelle valeur = ",newAdeqCost)
        addAdequacyCostInFortJSON(addressFortJSON,sectionCoordOfADEQUAOF, newAdeqCost)
    print("\n")

    #We modify the data of the VariantSet and store the data
    # in place of the former data. 
    VariantCSV = result(testAddress)
    createCSVFromDico(VariantCSV, testAddress)

if __name__ == "__main__":
    main(argv)
