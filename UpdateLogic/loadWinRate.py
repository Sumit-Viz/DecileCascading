#import pandas as pd
#from pandas import *
import numpy as np
import collections as col
import math,csv
import configparser;


def checkValidDecile(val):
    try:
        val1 = [int(ik) for ik in val.replace('A23_','').replace('"','').split('-')]
    except:
        return False
    try:
        if val1[0] <= 5 and val1[1] <= 5:
            return True
        else:
            return False
    except:
        return False

def checkFloat(val):
    try:
        val1 = float(val)
        if val1 > 0 :
            return val1
        else:
            return 0.0
    except:
        return 0.0

def updateAggrgateData(inJs,ky,newRowJson):
    global outJson
    if not "nonzeroBid" in inJs["overall"].keys():
        inJs["overall"] = {"nonzeroBid": checkFloat(newRowJson["nonzeroBid"]),"zeroBid": checkFloat(newRowJson["zeroBid"]),"Avg Bid Value" : checkFloat(newRowJson["Avg Bid Value"])*checkFloat(newRowJson["nonzeroBid"]),"Impressions" : checkFloat(newRowJson["Impressions"])}
    else:
        inJs["overall"]["nonzeroBid"] += checkFloat(newRowJson["nonzeroBid"])
        inJs["overall"]["zeroBid"] += checkFloat(newRowJson["zeroBid"])
	inJs["overall"]["Impressions"] += checkFloat(newRowJson["Impressions"])
	inJs["overall"]["Avg Bid Value"] += (checkFloat(newRowJson["nonzeroBid"]) * checkFloat(newRowJson["Avg Bid Value"]))
        
    if not ky.replace('A23_','') in inJs["decile_wise"]:
        inJs["decile_wise"][ky.replace('A23_','')] = {"nonzeroBid": checkFloat(newRowJson["nonzeroBid"]),"zeroBid": checkFloat(newRowJson["zeroBid"]),"Avg Bid Value" : checkFloat(newRowJson["Avg Bid Value"])*checkFloat(newRowJson["nonzeroBid"]),"Impressions" : checkFloat(newRowJson["Impressions"])} 
    else:
        inJs["decile_wise"][ky.replace('A23_','')]["nonzeroBid"] += checkFloat(newRowJson["nonzeroBid"])
        inJs["decile_wise"][ky.replace('A23_','')]["zeroBid"] += checkFloat(newRowJson["zeroBid"])
  	inJs["decile_wise"][ky.replace('A23_','')]["Avg Bid Value"] += (checkFloat(newRowJson["nonzeroBid"]) * checkFloat(newRowJson["Avg Bid Value"]))
	inJs["decile_wise"][ky.replace('A23_','')]["Impressions"] += checkFloat(newRowJson["Impressions"])



def gen_margin_factor_ds_csv():
        global campaign_name_to_id_dict,SaikuPub_to_RTBPub,outJson
        f = open('winRate.csv','rb')
        previousRowJson = {}
        for ind,row in enumerate(f):
            if ind > 0:
                row = row.strip().split(',')
                newRowJson = {}
                newRowJson["Campaign"] = campaign_name_to_id_dict.get(row[0].replace('"',''),"NoCampaignMap") if len(row[0].replace('"','')) != 0  else previousRowJson["Campaign"]
                newRowJson["Publisher"] = SaikuPub_to_RTBPub['saiku_rtb'].get(row[1].replace('"',''),'notFound')  if row[1].replace('"','') != "" else previousRowJson["Publisher"]
                if newRowJson["Publisher"] in ['rtbgoogle','rtb-google-auto']:
                    newRowJson["Publisher"] = 'Google'
                newRowJson["Experiment"] = row[2].replace('"','')  if row[2].replace('"','') != "" else previousRowJson["Experiment"]
                newRowJson["Sub Experiment"] = row[3].replace('"','') if row[3].replace('"','') != "" else previousRowJson["Sub Experiment"]
                newRowJson["nonzeroBid"] = row[4].replace('"','')
                newRowJson["zeroBid"] = row[5].replace('"','')
		newRowJson["Impressions"] = row[6].replace('"','')
                newRowJson["Avg Bid Value"] = row[7].replace('"','')
                previousRowJson = newRowJson
                pulisherType = 'WEB'
                if newRowJson["Publisher"].find('App') > -1 and  newRowJson["Publisher"].find('Appnexus') == -1:
                    pulisherType = 'APP'
                elif newRowJson["Publisher"].find('FBX') > -1:
                    pulisherType = 'FB'
                else:
                    pass
                keyTopLevel =  newRowJson["Campaign"]
                key =  newRowJson["Experiment"]
                if checkValidDecile(newRowJson["Sub Experiment"]):
                    if not keyTopLevel  in  outJson.keys():
                        outJson[keyTopLevel] = {"overall":{},"decile_wise":{}}
                    if not pulisherType in outJson[keyTopLevel].keys():
                        outJson[keyTopLevel][pulisherType]={"overall":{},"decile_wise":{}}
                    if not newRowJson["Publisher"]  in outJson[keyTopLevel][pulisherType].keys():
                        outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]]={"overall":{},"decile_wise":{}}
                    if not key  in outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]].keys():
                        outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]][key] = {"overall":{},"decile_wise":{}}
                    updateAggrgateData(outJson[keyTopLevel],newRowJson["Sub Experiment"],newRowJson)
                    updateAggrgateData(outJson[keyTopLevel][pulisherType],newRowJson["Sub Experiment"],newRowJson)
                    updateAggrgateData(outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]],newRowJson["Sub Experiment"],newRowJson)
                    updateAggrgateData(outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]][key],newRowJson["Sub Experiment"],newRowJson)
                    outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]][key]["decile_wise"][newRowJson["Sub Experiment"].replace('A23_','')] = {"nonzeroBid": checkFloat(newRowJson["nonzeroBid"]),"zeroBid": checkFloat(newRowJson["zeroBid"]),"Avg Bid Value" : checkFloat(newRowJson["Avg Bid Value"])*checkFloat(newRowJson["nonzeroBid"]),"Impressions" : checkFloat(newRowJson["Impressions"])}

def getRTBPublisherFromSaikuPubMap():
    outMap = {'rtb_saiku':{},'saiku_rtb':{}}
    for line in open('SaikuPub_to_RTBPub','r'):
        line1 = line.strip().split(',')
        outMap['saiku_rtb'][line1[1]] = line1[0]
        outMap['rtb_saiku'][line1[0]] = line1[1]
    outMap['saiku_rtb']['rtb-google-auto'] = 'Google'
    return outMap

def campaign_name_to_id():
        #print "Welcome to campaign_name_to_id"
        csv_file = open("advidtoadvname.csv")
        cv = csv.reader(csv_file, delimiter='\t')
        campaign_name_to_id_dict = {}
        for row in cv:
                campaign_name_to_id_dict[row[1]] = row[0]
        #print campaign_name_to_id_dict
        csv_file.close()
        return campaign_name_to_id_dict


keyListToIgnore = []
outJson = {}
SaikuPub_to_RTBPub = getRTBPublisherFromSaikuPubMap()
campaign_name_to_id_dict=campaign_name_to_id()
gen_margin_factor_ds_csv()
#print outJson['299']['FB']['FBX']
