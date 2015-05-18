

#import pandas as pd
#from pandas import *
import numpy as np
import collections as col
import math,csv
import configparser;
import loadWinRate as winrateData

def loadCampaignTarget():
    campTargetDict = {}
    f = open('auto-const-conf/auto-const-conf.ini','r')
    #f = configparser.ConfigParser()
    #f.read('auto-const-conf/auto-const-conf.ini') 
    #for key in f['ADVID_TO_CAMPAIGN'].keys():
	#campTargetDict[key] = json.loads(f['ADVID_TO_CAMPAIGN'][key])
    for l in f:
	l = l.strip().split('=')
	if len(l) ==2:
	    js = json.loads(l[1])
	    if (not campTargetDict.has_key(l[0])) and js['Finalize'] == '1':
		campTargetDict[l[0]] = js
    return campTargetDict

def pubAttributes(kyS,typ):
    ojs = {"pub":"","pubcat":"","advid":""}
    #print kyS
    if not typ in ["INTERCEPT","SRC","WEIGHT","CUTOFF"]:
        kyS.append('test')
    if 1: #typ in ["INTERCEPT","SRC"]:
        if len(kyS) == 4:
            ojs["advid"] = kyS[0]
        if len(kyS) ==5:
            ojs["pubcat"] = kyS[0]
            ojs["advid"] = kyS[1]
        if len(kyS) > 5:
            ojs["advid"] = kyS[-4]
            ojs["pubcat"] = kyS[-5]
            ojs["pub"] = "_".join(kyS[:-5])
    return ojs


def maxBidAttributes(kyS):
    ojs = {"pub":"","pubcat":"","advid":""}
    #print kyS
    if 1: #typ in ["INTERCEPT","SRC"]:
        if len(kyS) == 3:
            ojs["advid"] = kyS[-3]
        if len(kyS) ==4:
            ojs["pubcat"] = kyS[-4]
            ojs["advid"] = kyS[-3]
        if len(kyS) > 4:
            ojs["advid"] = kyS[-3]
            ojs["pubcat"] = kyS[-4]
            ojs["pub"] = "_".join(kyS[:-4])
    return ojs


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

def getKeyAttributes(ky):
    keySplit = ky.split('_')
    outjs={}
    if ky.find('A23_CVR') > -1 and ky.find('DECILE') == -1:
        outjs["typ"] = "CVR"
        if len(keySplit) >= 3  and ( not keySplit[-1] in ["INTERCEPT","DEF"]):
            outjs["advid"] = keySplit[-3]
            outjs["coeff_type"] = "COEFF"
        if len(keySplit) >=4  and keySplit[-1] == "INTERCEPT":
            outjs["advid"] = keySplit[-4]
            outjs["coeff_type"] = "INTERCEPT"
        if len(keySplit) >= 4  and keySplit[-1] == "DEF":
            try:
                outjs["advid"] = keySplit[-4]
            except:
                pass
            outjs["coeff_type"] = "DEF"
    elif ky.find('A23_CTR') > -1 and  ky.find('DECILE') == -1:
        outjs["typ"] = "CTR"
        if keySplit[-1] == "INTERCEPT":
            outjs["coeff_type"] = "INTERCEPT"
        elif keySplit[-1] == "SRC":
            outjs["coeff_type"] = "SRC"
        elif  keySplit[-1] == "CTR":
            outjs["coeff_type"] = "COEFF"
        else:
            outjs["coeff_type"] = keySplit[-1]
        #print ky
        pubAtt = pubAttributes(keySplit,outjs["coeff_type"])
        if not pubAtt["pubcat"] == "":
            outjs['pubcat'] = pubAtt["pubcat"]
        if not pubAtt["pub"] == "":
            outjs['pub'] = pubAtt["pub"]
        if not pubAtt["advid"] == "":
            outjs['advid'] = pubAtt['advid']
    elif ky.find('_DECILE_') > -1:
        outjs["typ"] = 'DECILE'
        if ky.find('DECILE_SRC') > -1:
            outjs["coeff_type"] = 'SRC'
        elif ky.find('DECILE_CUTOFF') > -1:
            outjs["coeff_type"] = 'CUTOFF'
        elif ky.find('DECILE_WEIGHT') > -1:
            outjs["coeff_type"] = 'WEIGHT'
        if ky.find('_CTR_CVR_') > -1:
            ky = ky.replace('CTR_CVR','CTRCVR').replace('DECILE_CUTOFF','DECILECUTOFF').replace('DECILE_WEIGHT','DECILEWEIGHT')
        ky = ky.replace('CTR_CVR','CTRCVR').replace('DECILE_CUTOFF','DECILECUTOFF').replace('DECILE_WEIGHT','DECILEWEIGHT')
        #print ky.split('_')
        pubAtt = pubAttributes(ky.split('_'),outjs["coeff_type"])
        if not pubAtt["pubcat"] == "":
            outjs['pubcat'] = pubAtt["pubcat"]
        if not pubAtt["pub"] == "":
            outjs['pub'] = pubAtt["pub"]
        if not pubAtt["advid"] == "":
            outjs['advid'] = pubAtt['advid']
    elif ky.find('_MAXBID') > -1:
        outjs["coeff_type"] = 'MAXBID'
        outjs["typ"] = "CTR"
        pubAtt = maxBidAttributes(ky.split('_'))
        #print ky,pubAtt
        if not pubAtt["pubcat"] == "":
            outjs['pubcat'] = pubAtt["pubcat"]
        if not pubAtt["pub"] == "":
            outjs['pub'] = pubAtt["pub"]
        if not pubAtt["advid"] == "":
            outjs['advid'] = pubAtt['advid']
        #print ky,outjs
        pass
    return outjs


    

def getDecileDict():
    outDict = {}
    global SaikuPub_to_RTBPub
    config = configparser.ConfigParser()
    config.optionxform=str
    config.read('intellibid-decile/intellibid-decile.ini')
    decileDict = {}
    for key in config['intellibid-decile'].keys():
	#print key
	keySplit = key.split('_')
	#print keySplit
	#print key,getKeyAttributes(key)
	pubKey = getKeyAttributes(key)
	if  pubKey.has_key('advid') and (not outDict.has_key(pubKey['advid'])):
	    outDict[pubKey['advid']] = {}
	if pubKey.has_key('pubcat') and (not outDict[pubKey['advid']].has_key(pubKey['pubcat'])):
	    outDict[pubKey['advid']][pubKey['pubcat']] = {}
	if pubKey.has_key('pub') and (not outDict[pubKey['advid']].get(pubKey.get('pubcat'),{}).has_key(pubKey.get('pub'))):
            outDict[pubKey['advid']][pubKey['pubcat']][pubKey['pub']] = {}
	if 1 :
	    if  pubKey.has_key('pubcat'):
                if pubKey.has_key('pub'):
                    outDict[pubKey['advid']][pubKey['pubcat']][pubKey['pub']][pubKey['coeff_type']] = config['intellibid-decile'][key]
                else:
                    outDict[pubKey['advid']][pubKey['pubcat']][pubKey['coeff_type']] = config['intellibid-decile'][key]
            else:
                outDict[pubKey['advid']][pubKey['coeff_type']] = config['intellibid-decile'][key]
    #print outDict['299']
    return outDict
	    
	    





 
def outputConfig(js):
    for key in campJson.keys():
        weight =[]
	kyList = key.split('|||')
        #print key
        if len(kyList) ==3:
            primaryKeyJson = {'campaign': kyList[2], 'publisher' : kyList[0], 'publisherType': kyList[1]}
            primaryKey = "_".join([primaryKeyJson['publisher'],primaryKeyJson['publisherType'],primaryKeyJson['campaign']])
            #print decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{})
            src = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get(primaryKeyJson['publisher'],{}).get('SRC')
            weightOld = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get(primaryKeyJson['publisher'],{}).get('WEIGHT')
            cutoff = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get(primaryKeyJson['publisher'],{}).get('CUTOFF')
        elif len(kyList) ==2:
            primaryKeyJson = {'campaign': kyList[1], 'publisherType': kyList[0]}
            primaryKey = "_".join([primaryKeyJson['publisherType'],primaryKeyJson['campaign']])
            src = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get('SRC')
            weightOld = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get('WEIGHT')
            cutoff = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get('CUTOFF')
        elif len(kyList) == 1:
            primaryKeyJson = {'campaign': kyList[0]}
            primaryKey = "_".join([primaryKeyJson['campaign']])
            src = decileDict.get(primaryKeyJson['campaign'],{}).get('SRC')
            weightOld = decileDict.get(primaryKeyJson['campaign'],{}).get('WEIGHT')
            cutoff = decileDict.get(primaryKeyJson['campaign'],{}).get('CUTOFF')
        else:
            src=None

        if src == 'CTR_CVR':
            for ctr_b in range(5):
                for cvr_b in range(5):
                    weight.append(str(campJson[key].get(str(ctr_b + 1) + '-' + str(cvr_b + 1),{}).get("finalWeight",1.0)))
	    print key.replace('|||','_') + '_DECILE_SRC=' + src
            print key.replace('|||','_') + '_' + src +  '_DECILE_CUTOFF=' + cutoff
            print key.replace('|||','_') + '_' + src +  '_DECILE_WEIGHT=' + ",".join(weight)
            #outputConfigEntry(key, src,weight)
        elif src in ['CVR','CTR']:
            weight = []
            for ctr_b in range(5):
                if src== 'CTR':
                    weight.append(str(campJson[key].get(str(ctr_b + 1) + '-0'  ,{}).get("finalWeight",1.0)))
                else:
                    weight.append(str(campJson[key].get('0-' + str(ctr_b + 1),{}).get("finalWeight",1.0)))
	    print key.replace('|||','_') + '_DECILE_SRC=' + src
            print key.replace('|||','_') + '_' + src +  '_DECILE_CUTOFF=' + cutoff
            print key.replace('|||','_') + '_' + src +  '_DECILE_WEIGHT=' + ",".join(weight)

            #outputConfigEntry(key, src,weight)
	
		


def checkFloat(val):
    try:
	val1 = float(val)
	if val1 > 0 :
	    return val1
	else:
	    return 0.0
    except:
	return 0.0


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

			

def updateAggrgateData(inJs,ky,newRowJson):
    global outJson
    if not "imp" in inJs["overall"].keys():
        inJs["overall"] = {"imp": checkFloat(newRowJson["Impressions"]),
                                                                            "click": checkFloat(newRowJson["Clicks"]),
                                                                            "sale_1day": checkFloat(newRowJson["Conversions one day"]),
                                                                           "sale" :checkFloat(newRowJson["Conversions"]),
                                                                           "cost" : checkFloat(newRowJson["Cost (CampCurr)"]),
                                                                           "revenue" : checkFloat(newRowJson["Booked Revenue (CampCurr)"]),
                                                                           "PPC" : checkFloat(newRowJson["ePPC (CampCurr)"])}
    else:
        inJs["overall"]["imp"] += checkFloat(newRowJson["Impressions"])
        inJs["overall"]["click"] += checkFloat(newRowJson["Clicks"])
        inJs["overall"]["sale_1day"] += checkFloat(newRowJson["Conversions one day"])
        inJs["overall"]["sale"] += checkFloat(newRowJson["Conversions"])
        inJs["overall"]["cost"] += checkFloat(newRowJson["Cost (CampCurr)"])
                        #print key, outJson[key]["overall"]["revenue"],checkFloat(newRowJson["Booked Revenue (INR)"])
        inJs["overall"]["revenue"] += checkFloat(newRowJson["Booked Revenue (CampCurr)"])
        inJs["overall"]["PPC"] = checkFloat(newRowJson["ePPC (CampCurr)"])
    if not ky.replace('A23_','') in inJs["decile_wise"]:
	inJs["decile_wise"][ky.replace('A23_','')] = {"imp": checkFloat(newRowJson["Impressions"]),
                                                                            "click": checkFloat(newRowJson["Clicks"]),
                                                                            "sale_1day": checkFloat(newRowJson["Conversions one day"]),
                                                                           "sale" :checkFloat(newRowJson["Conversions"]),
                                                                           "cost" : checkFloat(newRowJson["Cost (CampCurr)"]),
                                                                           "revenue" : checkFloat(newRowJson["Booked Revenue (CampCurr)"]),
                                                                           "PPC" : checkFloat(newRowJson["ePPC (CampCurr)"])}
    else:
	inJs["decile_wise"][ky.replace('A23_','')]["imp"] += checkFloat(newRowJson["Impressions"])
	inJs["decile_wise"][ky.replace('A23_','')]["click"] += checkFloat(newRowJson["Clicks"])
	inJs["decile_wise"][ky.replace('A23_','')]["sale_1day"] += checkFloat(newRowJson["Conversions one day"])
	inJs["decile_wise"][ky.replace('A23_','')]["sale"] += checkFloat(newRowJson["Conversions"])
	inJs["decile_wise"][ky.replace('A23_','')]["cost"] += checkFloat(newRowJson["Cost (CampCurr)"])
	inJs["decile_wise"][ky.replace('A23_','')]["revenue"] += checkFloat(newRowJson["Booked Revenue (CampCurr)"])
	inJs["decile_wise"][ky.replace('A23_','')]["PPC"] = checkFloat(newRowJson["ePPC (CampCurr)"])

	


def gen_margin_factor_ds_csv():
	global campaign_name_to_id_dict,SaikuPub_to_RTBPub,outJson
        f = open('decileCombined.csv','rb')
        #campaign_cpa = pd.read_excel("campaign_cpa.xls", "Sheet 1")
        #campaign_experiment_cpa = pd.read_excel("campaign_experiment_cpa.xls", "Sheet 1")
	previousRowJson = {}
        #outJson = {}
        for ind,row in enumerate(f):
	    if ind > 0:
	        row = row.strip().split(',')
	        #print row
	        newRowJson = {}
	        #print row
		#print previousRowJson
	        newRowJson["Campaign"] = campaign_name_to_id_dict.get(row[0].replace('"',''),"NoCampaignMap") if len(row[0].replace('"','')) != 0  else previousRowJson["Campaign"]
	        newRowJson["Payout Type"] = row[1].replace('"','') if row[1].replace('"','') != "" else previousRowJson["Payout Type"]
		newRowJson["Publisher"] = SaikuPub_to_RTBPub['saiku_rtb'][row[2].replace('"','')]  if row[2].replace('"','') != "" else previousRowJson["Publisher"]
		if newRowJson["Publisher"] in ['rtbgoogle','rtb-google-auto']:
		    newRowJson["Publisher"] = 'Google'
		#print newRowJson["Publisher"]
		#print row[2].replace('"','')
		newRowJson["Experiment IntelliBid"] = row[3].replace('"','')  if row[3].replace('"','') != "" else previousRowJson["Experiment IntelliBid"]
		newRowJson["Subexperiment IntelliBid"] = row[4].replace('"','') if row[4].replace('"','') != "" else previousRowJson["Subexperiment IntelliBid"]
		newRowJson["Impressions"] = row[5].replace('"','') 
		newRowJson["Clicks"] = row[6].replace('"','')
		newRowJson["Conversions"] = row[7].replace('"','')
	        newRowJson["Conversions one day"] = row[8].replace('"','')
		newRowJson["Cost (CampCurr)"] = row[10].replace('"','')
		newRowJson["Booked Revenue (CampCurr)"] = row[9].replace('"','')
		newRowJson["ePPC (CampCurr)"] = row[11].replace('"','')
		newRowJson["ePPA (CampCurr)"] = row[12].replace('"','')
	        #print newRowJson
		#if newRowJson["Publisher"] != previousRowJson.get("Publisher",'NA'):
		 #   print  newRowJson["Publisher"], previousRowJson.get("Publisher",'NA')
		previousRowJson = newRowJson
	        pulisherType = 'WEB'
		#print newRowJson["Publisher"]
	        if newRowJson["Publisher"].find('App') > -1 and  newRowJson["Publisher"].find('Appnexus') == -1:
		    pulisherType = 'APP'
		elif newRowJson["Publisher"].find('FBX') > -1:
		    pulisherType = 'FB'   
		else:
		    pass
		keyTopLevel =  newRowJson["Campaign"]
		key =  newRowJson["Experiment IntelliBid"]
		#print keyTopLevel,pulisherType,newRowJson["Publisher"],key, checkValidDecile(newRowJson["Subexperiment IntelliBid"])
		#print outJson[keyTopLevel]
		if checkValidDecile(newRowJson["Subexperiment IntelliBid"]):
		    #print newRowJson
		    if not keyTopLevel  in  outJson.keys():
			outJson[keyTopLevel] = {"overall":{},"decile_wise":{},"PayOut": newRowJson["Payout Type"]}
		    if not pulisherType in outJson[keyTopLevel].keys():
			outJson[keyTopLevel][pulisherType]={"overall":{},"decile_wise":{},"PayOut": newRowJson["Payout Type"]}
		    if not newRowJson["Publisher"]  in outJson[keyTopLevel][pulisherType].keys():
                        outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]]={"overall":{},"decile_wise":{},"PayOut": newRowJson["Payout Type"]}
		    if not key  in outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]].keys():
                        outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]][key] = {"overall":{},"decile_wise":{},"PayOut": newRowJson["Payout Type"]}
		    #print outJson
		    #print newRowJson
		    updateAggrgateData(outJson[keyTopLevel],newRowJson["Subexperiment IntelliBid"],newRowJson)
		    updateAggrgateData(outJson[keyTopLevel][pulisherType],newRowJson["Subexperiment IntelliBid"],newRowJson)
		    updateAggrgateData(outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]],newRowJson["Subexperiment IntelliBid"],newRowJson)
		    updateAggrgateData(outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]][key],newRowJson["Subexperiment IntelliBid"],newRowJson)
                    outJson[keyTopLevel][pulisherType][newRowJson["Publisher"]][key]["decile_wise"][newRowJson["Subexperiment IntelliBid"].replace('A23_','')] = {"imp": checkFloat(newRowJson["Impressions"]),
                                                                            "click": checkFloat(newRowJson["Clicks"]),
                                                                            "sale_1day": checkFloat(newRowJson["Conversions one day"]),
                                                                           "sale" :checkFloat(newRowJson["Conversions"]),
                                                                           "cost" : checkFloat(newRowJson["Cost (CampCurr)"]),
									   "revenue" : checkFloat(newRowJson["Booked Revenue (CampCurr)"]),
                                                                           "PPC" : checkFloat(newRowJson["ePPC (CampCurr)"])}
	

def getSegmentPerformance(campaignTarget,segData):
    payOutType = campaignTarget.get('Buisness_Model')
    #print segData
    perfAll = {}
    for key in segData.keys():
        if payOutType in ['CPS','CPA']:
            if segData[key]["sale_1day"] <= 1:
                if segData[key]["cost"] >= 3*campaignTarget['targetCPA']:
                    cpaPerf = 0.5
                else:
                    cpaPerf = 1.0
            else:
                cpaPerf = campaignTarget['targetCPA']/(segData[key]["cost"]/segData[key]["sale_1day"])
            perfAll[key] = {"cpaPerf" : cpaPerf}
   	elif payOutType == 'CPC':
            if segData[key]["sale_1day"] <= 2:
                if segData[key]["cost"] >= 3*campaignTarget['targetCPA']*segData[key]["sale_1day"]:
                    cpaPerf = 0.5
		    ppaPerf = 0.5
                else:
                    cpaPerf = 1.0
		    ppaPerf = 1.0
            else:
                cpaPerf = campaignTarget['targetCPA']/(segData[key]["cost"]/segData[key]["sale_1day"])
		ppaPerf = float(campaignTarget['Clnt1DayPPAExpt'])/(segData[key]["cost"]/segData[key]["sale_1day"])
            if segData[key]["click"] <= 10:
                if segData[key]["cost"] >= 2*campaignTarget['targetCPC']*segData[key]["click"] :
                    cpcPerf = 0.5
                elif segData[key]["cost"] <= 0.5*campaignTarget['targetCPC']*segData[key]["click"] :
                    cpcPerf = 2.0
                else:
            	    cpcPerf = 1.0
            else:
                cpcPerf = campaignTarget['targetCPC']/(segData[key]["cost"]/segData[key]["click"])
            perfAll[key] = {"cpaPerf" : cpaPerf,"cpcPerf":cpcPerf,"ppaPerf" : ppaPerf}
        else:
            perfAll[key] = {}
    return perfAll



def getkeyWeight(keyIn,inJson,topLevelJson,campaignTarget):
    global campaignTargetDict
    global decileDict
    global outJson,testKey
    #print keyIn
    bucPosCTR,bucPosCVR =  [int(ik) for ik in keyIn.split('-')]
    payOutType = campaignTarget.get('Buisness_Model','CPC')
    campData = inJson["overall"]
    bucData  =  inJson['decile_wise'][keyIn]
    if campData["imp"] <=0. or  campData["click"] <=0. or  campData["sale_1day"] <=0. :
        return '1.0'
    else:
	topLevelCPA = topLevelJson["cost"]/topLevelJson["sale_1day"]
        campCPA = campData["cost"]/campData["sale_1day"]
        if not bucData["sale_1day"] == 0 :
            bucCPA = bucData["cost"]/bucData["sale_1day"]
        else:
            bucCPA = campCPA
	topLevelCPC = topLevelJson["cost"]/topLevelJson["click"]
        campCPC = campData["cost"]/campData["click"]
        if  bucData["click"] > 0 :
            bucCPC = bucData["cost"]/bucData["click"]
        else:
            bucCPC = campCPC
    targetCPC = 0.0
    if payOutType == 'CPS':
	payOutType ='CPA'
    if payOutType == 'CPC':
        keysOfInterest = [(1,1),(1,2),(1,3),(1,4),(1,5),(2,1),(2,2),(2,3)]
	campMargin = (campData["revenue"] - campData["cost"])/campData["revenue"]
	#targetCPC = 0.9*campData["revenue"]/campData["click"]
        targetCPC = campaignTarget['targetCPC']
	targetCPA = campaignTarget['targetCPA']
	topLevelTargetCPC = 0.9*topLevelJson["revenue"]/topLevelJson["click"]
	#if campCPC >= targetCPC:
	  #  campCPC = targetCPC
	    
    elif payOutType == 'CPA':
        keysOfInterest = [(1,1),(2,1),(3,1),(4,1),(5,1),(1,2)]
	targetCPA = campaignTarget['targetCPA']
    else:
        pass
    bucketTuple = (int(bucPosCTR),int(bucPosCVR))
    if bucPosCVR ==0.0:
	bucPosCVR = 1.0
    if bucPosCTR == 0.0:
	bucPosCTR = 1.0
    if payOutType == 'CPA':
        CPAFactor = 1.0/bucPosCVR
    else:
        CPAFactor =1.0
    CPCFactor = 1.0
    if payOutType in ['CPA','CPC','CPS'] and len([ik for ik in keysOfInterest if bucketTuple[0] == ik[0] and  bucketTuple[1] == ik[1]]) ==1:
        if not bucData["sale_1day"] <=1:
            CPAFactor = math.sqrt(targetCPA/bucCPA)
        else:
            CPAFactor = 1.0
        if  bucData["click"] >=10  and payOutType == 'CPC':
            CPCFactor = max([targetCPC/bucCPC,0.5])
        else:
            CPCFactor = 1.0
    else:
        if payOutType == 'CPC' and bucData["click"] >=20:
             CPCFactor = targetCPC/bucCPC
	if payOutType == 'CPA' and  bucData["sale_1day"] >=2:
	     CPAFactor = math.sqrt(targetCPA/bucCPA)
	elif payOutType == 'CPA' and  bucData["sale_1day"] >=1:
	     CPAFactor = math.sqrt(math.sqrt(targetCPA/bucCPA))
    #print testKey,keyIn +'###',bucCPC,campCPC,topLevelCPC,bucCPA,campCPA,topLevelCPA,CPAFactor,CPCFactor, CPAFactor*CPCFactor,bucData["click"],campData["click"],topLevelJson["click"],bucData["sale_1day"],campData["sale_1day"],topLevelJson["sale_1day"]
    return CPAFactor*CPCFactor


def getNormalizedFactor(decilePerformance,payOut,segPerformance,bucWinRate):
    perfCutoff = 1.15
    winRateCutoff = 0.55
    CPAFactor = 1.0
    CPCFactor = 1.0
    winRateFactor = 1.0
    if payOut in ['CPA','CPS']:
	if segPerformance["campaign"]["cpaPerf"] >= perfCutoff:
	    if decilePerformance["decile"]["cpaPerf"] <= 1.0:
	        if decilePerformance["decile"]["cpaPerf"] >= 1.0/perfCutoff:
	            CPAFactor = 1.0
		else:
		    CPAFactor = math.sqrt(decilePerformance["decile"]["cpaPerf"] * segPerformance["campaign"]["cpaPerf"])
	    else:
		if bucWinRate["winRate"] > winRateCutoff:
		    CPAFactor = 1.0
		else:
		    winRateFactor = (1. + (winRateCutoff - bucWinRate["winRate"])/winRateCutoff)
		    CPAFactor = math.sqrt(decilePerformance["decile"]["cpaPerf"])
	else:
	    if decilePerformance["decile"]["cpaPerf"] <= 1.0:
		CPAFactor = math.sqrt(decilePerformance["decile"]["cpaPerf"])
	    else:
		if bucWinRate["winRate"] > winRateCutoff:
                    CPAFactor = 1.0
                else:
                    winRateFactor =(1. + (winRateCutoff - bucWinRate["winRate"])/winRateCutoff)
                    CPAFactor = math.sqrt(decilePerformance["decile"]["cpaPerf"])
	#return {"CPAFactor":CPAFactor,"CPCFactor" :CPCFactor,"winRateFactor":winRateFactor}
    elif payOut == 'CPC':
	if segPerformance["campaign"]["ppaPerf"] >= perfCutoff:
            if decilePerformance["decile"]["ppaPerf"] <= 1.0:
                if decilePerformance["decile"]["ppaPerf"] >= 1.0/perfCutoff:
                    CPAFactor = 1.0
                else:
                    CPAFactor = math.sqrt(decilePerformance["decile"]["ppaPerf"] * segPerformance["campaign"]["ppaPerf"])
            else:
                if bucWinRate["winRate"] > winRateCutoff:
                    CPAFactor = 1.0
                else:
                    winRateFactor = 1. + (winRateCutoff - bucWinRate["winRate"])/winRateCutoff
                    CPAFactor = math.sqrt(decilePerformance["decile"]["ppaPerf"])
	else:
	    if decilePerformance["decile"]["ppaPerf"] <= 1.0:
                CPAFactor = math.sqrt(decilePerformance["decile"]["ppaPerf"])
            else:
                if bucWinRate["winRate"] > winRateCutoff:
                    CPAFactor = 1.0
                else:
                    winRateFactor =(1. + (winRateCutoff - bucWinRate["winRate"])/winRateCutoff)
                    CPAFactor = math.sqrt(decilePerformance["decile"]["ppaPerf"])

	if segPerformance["campaign"]["cpcPerf"] >= perfCutoff:
            if decilePerformance["decile"]["cpcPerf"] <= 1.0:
                if decilePerformance["decile"]["cpcPerf"] >= 1.0/perfCutoff:
                    CPCFactor = 1.0
                else:
                    CPCFactor = math.sqrt(decilePerformance["decile"]["cpcPerf"] * segPerformance["campaign"]["cpcPerf"])
            else:
                if bucWinRate["winRate"] > winRateCutoff:
                    CPCFactor = 1.0
                else:
                    winRateFactor = 1. + (winRateCutoff - bucWinRate["winRate"])/winRateCutoff
                    CPCFactor = math.sqrt(decilePerformance["decile"]["cpcPerf"])
	else:
	    if decilePerformance["decile"]["cpcPerf"] <= 1.0:
                CPCFactor = math.sqrt(decilePerformance["decile"]["cpcPerf"])
            else:
                if bucWinRate["winRate"] > winRateCutoff:
                    CPCFactor = 1.0
                else:
                    winRateFactor =(1. + (winRateCutoff - bucWinRate["winRate"])/winRateCutoff)
                    CPCFactor = math.sqrt(decilePerformance["decile"]["cpcPerf"])

    print {"CPAFactor":CPAFactor,"CPCFactor" :CPCFactor,"winRateFactor":winRateFactor}
    return {"CPAFactor":CPAFactor,"CPCFactor" :CPCFactor,"winRateFactor":winRateFactor}



def getkeyWeight1(keyIn,inJson,topLevelJson,campaignTarget,segPerf,winrateSummary):
    global wrData,decileDict,outJson
    bucPosCTR,bucPosCVR =  [int(ik) for ik in keyIn.split('-')]
    bucketTuple = (int(bucPosCTR),int(bucPosCVR))
    payOutType = campaignTarget.get('Buisness_Model','CPC')
    bucData  =  inJson['decile_wise'][keyIn]
    campData = inJson["overall"]
    if campData["imp"] <=0. or  campData["click"] <=0. or  campData["sale_1day"] <=0. :
        return '1.0'
    if payOutType == 'CPS':
        payOutType ='CPA'
    if payOutType == 'CPC':
        keysOfInterest = [(1,1),(1,2),(1,3),(1,4),(1,5),(2,1),(2,2),(2,3)]
    elif payOutType == 'CPA':
	keysOfInterest = [(1,1),(2,1),(3,1),(4,1),(5,1),(1,2)]
    else:
	keysOfInterest = []
    try:
        CPAFactor = 1.0/bucPosCVR if payOutType == 'CPA' else 1.0
    except:
	CPAFactor = 1.0
    CPCFactor = 1.0
    if not keyIn in winrateSummary.get("decile_wise",{}).keys():
 	bucWinRate = {"winRate":0.0,"bidRate":0.0}
    else:
        bucWinRate = {"winRate" : winrateSummary["decile_wise"][keyIn]["Impressions"]/( winrateSummary["decile_wise"][keyIn]["nonzeroBid"] + 1.),"bidRate" : ( winrateSummary["decile_wise"][keyIn]["nonzeroBid"])/( winrateSummary["decile_wise"][keyIn]["nonzeroBid"] +  1. + winrateSummary["decile_wise"][keyIn]["zeroBid"])}
    decilePerf = getSegmentPerformance(campaignTarget,{"decile":inJson["decile_wise"][keyIn]})
    factorJson = getNormalizedFactor(decilePerf,payOutType,segPerf,bucWinRate)
    #{"CPAFactor":CPAFactor,"CPCFactor" :CPCFactor,"winRateFactor":winRateFactor}
    #print decilePerf,segPerf["campaign"]
    if payOutType == 'CPA':
	return max(min( factorJson["winRateFactor"], factorJson["CPAFactor"] * factorJson["winRateFactor"]),0.5)
    elif payOutType == 'CPC':
        topLevelPerf = {}
	if len(segPerf.keys()) ==3:
	    topLevelPerf = segPerf["publisher"]
 	elif len(segPerf.keys()) ==2:
	    topLevelPerf = segPerf["pubType"]
	else:
	    topLevelPerf = segPerf["campaign"]
	if topLevelPerf["ppaPerf"] > 1. :
	    return max(min( factorJson["winRateFactor"] , factorJson["CPAFactor"] * factorJson["winRateFactor"]),0.5)
	else:
	    return max(min( factorJson["winRateFactor"] , factorJson["CPAFactor"] * factorJson["winRateFactor"] * factorJson["CPCFactor"]),0.5) 
    return '1.0'
   
    


def getCampaignTarget(inJS):
    ppa = float(inJS.get('Clnt1DayPPAExpt','100.00'))
    if ppa == 0.0:
	ppa = 100.0
    margin = float(inJS.get('Margin_Target','20.00'))
    if margin == 0.0:
	margin = 20.0
    ppc = float(inJS.get('ClntPPAExpt','10.00'))
    if inJS.get('Buisness_Model') in ['CPA','CPS']:
	inJS['targetCPA'] = ppa * ( 1. - margin/100. )
    elif inJS.get('Buisness_Model') == 'CPC':
	inJS['targetCPA'] = ppa * ( 1. - margin/100. )
	inJS['targetCPC'] = ppc * ( 1. - margin/100. )
    return inJS

def getFinalWeight(kyList, inJson,topLevelJson1):
    global campaignTargetDict,wrData
    expJson = {}
    keys = inJson['decile_wise'].keys()
    campaignTarget = getCampaignTarget(campaignTargetDict.get(kyList[-2],{}))
    #print kyList,campaignTarget
    if len(kyList) ==4 :
	primaryKeyJson = {'campaign': kyList[2], 'publisher' : kyList[0], 'publisherType': kyList[1],'experiment': kyList[3]}
	primaryKey = "_".join([primaryKeyJson['publisher'],primaryKeyJson['publisherType'],primaryKeyJson['campaign']])
	#print decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{})
	src = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get(primaryKeyJson['publisher'],{}).get('SRC')
	weight = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get(primaryKeyJson['publisher'],{}).get('WEIGHT')
        winrateSummary = wrData.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get(primaryKeyJson['publisher'],{})
	topLevelJson = topLevelJson1["pubType"]
	#perf = getSegmentPerformance(campaignTarget,topLevelJson1["publisher"])
    elif len(kyList) ==3:
	primaryKeyJson = {'campaign': kyList[1], 'publisherType': kyList[0],'experiment':kyList[2]}
	primaryKey = "_".join([primaryKeyJson['publisherType'],primaryKeyJson['campaign']])
	src = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get('SRC')
	weight = decileDict.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{}).get('WEIGHT')
	winrateSummary = wrData.get(primaryKeyJson['campaign'],{}).get(primaryKeyJson['publisherType'],{})
	topLevelJson = topLevelJson1["campaign"]
	#perf = getSegmentPerformance(campaignTarget,topLevelJson1["pubType"])
    elif len(kyList) == 2:
	primaryKeyJson = {'campaign': kyList[0],'experiment': kyList[1]}
	primaryKey = "_".join([primaryKeyJson['campaign']])
	src = decileDict.get(primaryKeyJson['campaign'],{}).get('SRC')
	weight = decileDict.get(primaryKeyJson['campaign'],{}).get('WEIGHT')
        winrateSummary = wrData.get(primaryKeyJson['campaign'],{})
	topLevelJson = topLevelJson1["campaign"]
	#perf = getSegmentPerformance(campaignTarget,topLevelJson1["campaign"])
    else:
	return {}
    segPerf  = getSegmentPerformance(campaignTarget,topLevelJson1)
    #print kyList,src,weight,segPerf
    weightJson = {}
    if src:
	#print kyList,src,weight
	#print primaryKey
	weightJson = {}
	weightList = weight.split(',')
	if src =='CTR_CVR':
	    for ctr_b in range(1,6):
		for cvr_b in range(1,6):
		    weightJson[str(ctr_b) + '-' + str(cvr_b)] = weightList[(ctr_b-1)*5 + cvr_b - 1]
	else:
	    for ctr_b in range(1,6):
		keyBucket = '0-' + str(ctr_b) if src == 'CVR' else str(ctr_b) + '-0'
		weightJson[keyBucket] = weightList[ctr_b -1]
    for key in keys:
        if  src in ['CTR_CVR','CVR','CTR']:
	    #keyIn,inJson,topLevelJson,campaignTarget,segPerf,winrateSummary
            #weightNew = getkeyWeight(key,inJson,topLevelJson,campaignTarget)
	  #  print kyList,key,src,segPerf
	    if src == 'CTR_CVR' and key.find('0') > -1:
	        weightNew = 1.0
	    else:
	        weightNew = getkeyWeight1(key,inJson,topLevelJson,campaignTarget,segPerf,winrateSummary)
            try:
                oldWeight = float(weightJson.get(str(key),'1.0'))
                finalWeight =  float(weightNew)*oldWeight
            except:
                finalWeight = 1.0
            weight = weightNew
            expJson[key] = {"weight":weightNew,"finalWeight":finalWeight,"oldWeight":oldWeight}
	    #print primaryKey,key,expJson[key]
	    #print [primaryKey,str(key) + '##',inJson["decile_wise"][key]["imp"],inJson["decile_wise"][key]["click"],inJson["decile_wise"][key]["sale_1day"],inJson["decile_wise"][key]["cost"],inJson["overall"]["imp"],inJson["overall"]["click"],inJson["overall"]["sale_1day"],inJson["overall"]["cost"],str(weight),oldWeight]
            print "\t".join([str(ik) for ik in [primaryKey,str(key) + '##',inJson["decile_wise"][key]["imp"],inJson["decile_wise"][key]["click"],inJson["decile_wise"][key]["sale_1day"],inJson["decile_wise"][key]["cost"],inJson["overall"]["imp"],inJson["overall"]["click"],inJson["overall"]["sale_1day"],inJson["overall"]["cost"],str(weight),oldWeight,campaignTarget.get('targetCPA',0.0),campaignTarget.get('targetCPC',0.0),campaignTarget.get('Clnt1DayPPAExpt',0.0)]])
    for key in weightJson.keys():
        if not key in expJson.keys():
            expJson[key] = {"weight":'1.0',"finalWeight":weightJson.get(key,'1.0'),"oldWeight":weightJson.get(key,'1.0')}
    return expJson




keyListToIgnore = []
outJson = {}  
SaikuPub_to_RTBPub = getRTBPublisherFromSaikuPubMap()
campaign_name_to_id_dict=campaign_name_to_id()        
decileDict = getDecileDict()
campaignTargetDict = loadCampaignTarget()
#outJson = i
gen_margin_factor_ds_csv()
wrData = winrateData.outJson
#print wrData['1306']['FB']['FBX']
#print outJson['1306']['FB']
test_key = 'JP_benesse_MW_rtb-google-auto_A23'
#print outJson[test_key]
#keys = outJson[test_key]['decile_wise'].keys()
#inJson = outJson[test_key]
#decileDict()


eL = ['decile_wise','overall','PayOut']
campJson = {}
for campaign in outJson.keys():
    if not campaign in eL:
	if outJson[campaign]["overall"]["imp"] > 1000:
	    extraJson = {"campaign":outJson[campaign]["overall"]}
	    campJson[campaign ] = getFinalWeight([campaign,experiment],outJson[campaign] ,extraJson)
        for pulisherType in outJson[campaign].keys():
	    if not pulisherType in eL:
		experiment = 'A23'
		if not (campaign in eL or pulisherType in eL or  experiment in eL):
		    #print campaign,pulisherType,experiment,outJson[campaign][pulisherType]
		    if outJson[campaign][pulisherType]["overall"]["imp"] > 1000:	        
		        extraJson = {"campaign":outJson[campaign]["overall"],"pubType":outJson[campaign][pulisherType]["overall"]}
			campJson[pulisherType + '|||' + campaign ] = getFinalWeight([pulisherType,campaign,experiment] ,outJson[campaign][pulisherType],extraJson)
	        for publisher in outJson[campaign][pulisherType].keys():
	            if not publisher in eL:
	        	for experiment in outJson[campaign][pulisherType][publisher].keys():
		    	    if not (campaign in eL or pulisherType in eL or publisher in eL or experiment in eL):
				testKey =  "_".join([publisher,pulisherType,campaign,experiment])
		        	if outJson[campaign][pulisherType][publisher][experiment]["overall"]["imp"] > 1000:
				    extraJson = {"pubType":outJson[campaign][pulisherType]["overall"],"campaign":outJson[campaign]["overall"],"publisher":outJson[campaign][pulisherType][publisher][experiment]["overall"]}
				    campJson[publisher + '|||' + pulisherType + '|||' + campaign] = getFinalWeight([publisher,pulisherType,campaign,experiment] ,outJson[campaign][pulisherType][publisher][experiment],extraJson)
#print [ik for ik in campJson.keys() if ik.find('299') > -1]
outputConfig(campJson)
