/*
 * ####################################### DECILING - JAVA CODE #############################################
 * ### Author(s) : Shivam Gupta, Sumit Khanna															  ###
 * ### Project : Intellibid (Sub-part :: Deciling / Weights Update)										  ###
 * ### DOC !																							  ###
 * ###																									  ###
 * ### Intent :-																						  ###	
 * ###																									  ###
 * ### To Read in the following :																		  ###
 * ### 1. From Saiku :																					  ###
 * ### 1.1 CUBE : RTBFunnel | Data : Zbids, NZbids, Impr, Avg Bid Value									  ###
 * ### 1.2 CUBE : Metrics	| Data : Impr,Click,Conversions,ConversionsOneDay,Revenue,Cost,ePPC,ePPA	  ###
 * ### NOTE : All these values are aggregated at the following level :-									  ###
 * ### Campaign,Publisher,Payout Type, Exp(A23)															  ###
 * ###																									  ###
 * ### 2. From s3://datascience																			  ###
 * ### 2.1 decile.INI																					  ###
 * ### 2.2 auto-cons-conf.INI																			  ###
 * ### NOTE : 																							  ###
 * ### decile.INI : contains MAXBID / SRC / DECILE CUTOFF / DECILE WEIGHTS @ publ-plat-adv-exp level	  ###
 * ### auto-cons-conf.INI : contains Adv level attribs, as a JSON format								  ###
 * ###																									  ###
 * ### Process :-																						  ###
 * ###																									  ###
 * ### 1// Read the decile.INI file, line-by-line														  ###
 * ### First rows are about the advids enlisted, just record keep them									  ###
 * ### Then, parse the key values, one by one, and insert them as a branch in the base tree, 			  ###
 * ### Wherein, the tree is basically a Hierarchy of PUBLISHER,PLATFORMS,CAMPAIGNS						  ###
 * ### Insert along with the leaf node, the attribs like MAXBID / SRC / DECILE-CUTOFF / DECILE-WEIGHTS	  ###
 * ### 																									  ###
 * ### 2// Read the cons-conf.INI file, line-by-line													  ###
 * ### stringify these jsons, and then record-keep these properties to be used later in the logic		  ###
 * ### 																									  ###
 * ### 3// Read the csvs procured fro Saiku 															  ###
 * ### Those csvs are conversions from jsons obtained from the saiku python scripts 					  ###
 * ### Simply put, the process is to keep a query with your folder in pivot								  ###
 * ### Then using a python utility script, rerun results from saiku, results being returned ads JSONs	  ###
 * ### Parse the csv much the same way we did for 1// and 2//											  ###
 * ###																									  ###
 * ### 4// Apply a recursive code, to build the tree bottom up, with parents acquiring values aggregated  ###
 * ### at their children. We herein, apply different logic for populating the Maps of the parent node 	  ###
 * ### from their children.																				  ###
 * ###																									  ###
 * ### 5// Update the weights , either hardcoded, or the logic build-up									  ###
 * ### 6// print the updated weights and records to an output file										  ###
 * ### 																									  ###
 * ### THAT'S IT!!!																						  ###
 * ##########################################################################################################
 * 
 */

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class decileTreeBuilder {
    /*
     * filename for intellibid-decile.ini
     */
    private static String decilefile;
    /*
     * filename for auto-const-conf.ini
     */
    private static String advInfoFile;
    /*
     * the bids.json -> csv converted file
     */
    private static String bidscsvfile;
    /*
     * the cost.json -> csv converted file
     */
    private static String costcsvfile;
    /*
     * the output file
     */
    private static String outputfile;
    /*
     * the output writer
     */
    private static BufferedWriter outwriter = null;
    /*
     * reads the intellibid-decile.ini
     */
    private static BufferedReader decileReader = null;
    /*
     * reads the auto-const-conf.ini
     */
    private static BufferedReader advInfoReader = null;
    /*
     * bids.csv reader
     */
    private static BufferedReader bidsSaikuReader = null;
    /*
     * cost.csv reader
     */
    private static BufferedReader costSaikuReader = null; 
    /*
     * storing decile weights/cutoffs
     */
    private static HashMap<String, String> decileMap = new HashMap<String,String>();
    /*
     * storing advids list
     */
    private static HashMap<String, ArrayList<String>> advidsMap = new HashMap<String,ArrayList<String>>();

    private static HashMap<String, HashMap<String,String>> advInfoMap = new HashMap<String,HashMap<String,String>>();//donot know where it gets used, maybe logic
    /*
     * the main tree
     */
    private static TreeNode root = null;
    private static ArrayList<String> iniKeyHash = new ArrayList<String>();
    /*
     * flip-flop to chose the map
     */
    enum decileMaps { advidsMap,decileMap };
    /*
     * main function
     * the only keys to be written in the decile INI file
     * populate the files - decilefile & advInfoFile
     */

    /*
     * ########################################################################################################
     * ### 	WALKTHROUGH ! 																					###
     * ###  main()																							###
     * ###  --> initializeWriteKeys()																		###
     * ###		add MAXBIDS,DECILE_SRC, CTR_CVR_DECILE_CUTOFFS,CTR_CVR_DECILE_WEIGHTS						###
     * ###  --> buildInfoMap()																				###
     * ###		decilefile																					###
     * ###      -- advidsmap																				###
     * ###		-- decilemap																				###
     * ###      advinfofile																					###
     * ###		--> createMapKV // for JSON parsing 														###
     * ###  --> buildTree()																					###
     * ###      create root																					###
     * ### 		--> insertBranch()																			###
     * ###			rootCrawl																				###
     * ###			existsNode()																			###
     * ###			populate the branch's hashmap															###
     * ###	-->	getbids()																					###
     * ###	--> getcosts()																					###
     * ###  --> updateWeights()																				###
     * ###	--> printINI()																					###
     * ########################################################################################################
     */ 

    public static void main(String[] args) {
        intiliazeWriteKeys();
        buildInfoMap(); 

        /*Now that we have read the weights and advInfo files :- 
         *Let us costruct the tree .1
         *And stick data onto it   .2
         */

        /*
         * the tree has been built, the stage has been set
         */
        buildTree();

        /*
         * next intent is to either build/grow the same tree,
         * or populate a different tree with bids and costs SAIKU data
         */
        getBids();
        getCosts();

        // update weights
        updateWeights(root);
        // this populates values bottom up from children node to parent node , upto the root
        bottomUpFillTree(root);

        printINI(root);
    }
    // we only have , at max these keys in the decileINI file
    private static void intiliazeWriteKeys() {
        iniKeyHash.add("MAXBID");
        iniKeyHash.add("DECILE_SRC");
        iniKeyHash.add("CTR_CVR_DECILE_CUTOFF");
        iniKeyHash.add("CTR_CVR_DECILE_WEIGHT");
    }
    // update the weights
    private static void updateWeights(TreeNode rootnode) {
        if(rootnode == null)
        {
            System.out.println("[ERROR]The tree is empty");
        }
        else if(rootnode.curr == 0)
        {
            String weights = rootnode.attribs.get("CTR_CVR_DECILE_WEIGHT");
            String src = rootnode.attribs.get("DECILE_SRC");

            String wts_ctr = null;
            String wts_cvr = null;

            if(src.equalsIgnoreCase("CTR_CVR"))
            {
                String[] wts = weights.split("_");
                wts_ctr = wts[0];
                wts_cvr = wts[1];
            }
            else if(src.equalsIgnoreCase("CTR"))
            {
                wts_ctr = new String(weights);
            }
            else if(src.equalsIgnoreCase("CVR"))
            {
                wts_cvr = new String(weights);
            }

            String updatedWeightsCTR = "";
            String updatedWeightsCVR = "";

            if(wts_cvr!=null){
                String[] weights_cvr = wts_cvr.split(",");
                ArrayList<Double> cvr_weightlist = new ArrayList<Double>();
                for(String wt : weights_cvr)
                {
                    cvr_weightlist.add(1.1*Double.parseDouble(wt));
                }
                for(double d : cvr_weightlist)
                {
                    updatedWeightsCVR += Double.toString(d);
                    updatedWeightsCVR += ",";
                }
                updatedWeightsCVR = updatedWeightsCVR.substring(0, updatedWeightsCVR.length()-1);
                if(src.equals("CVR"))
                    rootnode.attribs.put("CTR_CVR_DECILE_WEIGHT",updatedWeightsCVR);
            }
            if(wts_ctr!=null){
                String[] weights_ctr = wts_ctr.split(",");
                ArrayList<Double> ctr_weightlist = new ArrayList<Double>();
                for(String wt : weights_ctr)
                {
                    ctr_weightlist.add(1.1*Double.parseDouble(wt));
                }
                for(double d : ctr_weightlist)
                {
                    updatedWeightsCTR += Double.toString(d);
                    updatedWeightsCTR += ",";
                }
                updatedWeightsCTR = updatedWeightsCTR.substring(0, updatedWeightsCTR.length()-1);
                if(src.equals("CTR"))
                    rootnode.attribs.put("CTR_CVR_DECILE_WEIGHT",updatedWeightsCTR);
            }
            if(src.equalsIgnoreCase("CTR_CVR"))
            {
                String updatedWeights = updatedWeightsCTR+"_"+updatedWeightsCVR;
                rootnode.attribs.put("CTR_CVR_DECILE_WEIGHT", updatedWeights);
            }
        }
    }
    // generate the decileINI file
    private static void printINI(TreeNode rootnode) {
        outputfile = "/home/sumitkhanna/Desktop/Desktop/Work/DecilingCascade/test/updatedDecile.ini";
        try {

            File outfile = new File(outputfile);

            if (!outfile.exists()) {
                outfile.createNewFile();
            }

            outwriter = new BufferedWriter(new FileWriter(outfile.getAbsoluteFile()));

            printUtil(root,new String[10],0);

            outwriter.close();

        } catch (IOException e) {
            System.out.println("[EXCEPTION] Could not write to the output file");
        }
    }
    // a helper to generate decileINI file
    private static void printUtil(TreeNode rootnode, String[] path, int len) {
        // Prints all paths to leaf  
        if ( rootnode == null )  
            return;  

        // storing data in array  
        path[len] = rootnode.identifierLvl;  
        len++;  

        if(rootnode.curr == 0) {  
            // leaf node is reached  
            printNodeMap(rootnode,path,len);  
            return;  
        }  
        for(TreeNode child : rootnode.children){
            printUtil(child, path, len);  
            printUtil(child, path, len);
        }
    }

    // the helper print function to print the rows corresponding to every tree node leaf
    private static void printNodeMap(TreeNode rootnode, String[] path, int len) {
        String part = "";
        for(int i = 1; i< len;i++)
        {
            part+=path[i]+"_";
        }
        part+="A23_";
        for(Map.Entry<String, String> e : rootnode.attribs.entrySet())
        {
            String partsub = new String(part);
            if(containsKeys(e.getKey(),iniKeyHash ))
            {
                partsub += e.getKey();
                partsub+="=";
                partsub+=e.getValue();
                try {
                    System.out.println(partsub);
                    outwriter.write(partsub);
                } catch (IOException e1) {
                    System.out.println("[EXCEPTION]Problems writing to the output file");
                }
            }
        }
    }

    private static boolean containsKeys(String key,
            ArrayList<String> iniKeyHash2) {
        boolean found = false;
        for(String s : iniKeyHash2)
        {
            if(s.equalsIgnoreCase(key))
            {
                found = true;
            }
        }
        return found;
    }
    // populate the tree bottom up
    private static void bottomUpFillTree(TreeNode rootnode) {
        if(rootnode == null || rootnode.curr == 0)
        {
            // skip - do nothing
        }
        for(TreeNode node : rootnode.children)
        {
            bottomUpFillTree(node);
        }
        //logic for NZBids,ZBids,impressions,clicks,conversions,conversionsOneDay,revenue,cost
        double sumNZBids = 0;
        double sumZBids = 0;
        double sumImpressions = 0;
        double sumClicks = 0;
        double sumConversions = 0;
        double sumConversionsOneDay = 0;
        double sumRevenue = 0;
        double sumCost = 0;

        for(TreeNode node : rootnode.children)
        {
            sumNZBids += Double.parseDouble(node.attribs.get("NonZeroBid"));
            sumZBids += Double.parseDouble(node.attribs.get("ZeroBid"));
            sumImpressions += Double.parseDouble(node.attribs.get("impressions"));
            sumClicks += Double.parseDouble(node.attribs.get("clicks"));
            sumConversions += Double.parseDouble(node.attribs.get("conversions"));
            sumConversionsOneDay += Double.parseDouble(node.attribs.get("conversionsOneDay"));
            sumRevenue += Double.parseDouble(node.attribs.get("revenue"));
            sumCost += Double.parseDouble(node.attribs.get("cost"));
        }
        rootnode.attribs.put("NonZeroBid", Double.toString(sumNZBids));
        rootnode.attribs.put("ZeroBid",Double.toString(sumZBids));
        rootnode.attribs.put("impressions", Double.toString(sumImpressions));
        rootnode.attribs.put("clicks", Double.toString(sumClicks));
        rootnode.attribs.put("conversions",Double.toString(sumConversions));
        rootnode.attribs.put("conversionsOneDay",Double.toString(sumConversionsOneDay));
        rootnode.attribs.put("revenue",Double.toString(sumRevenue));
        rootnode.attribs.put("cost", Double.toString(sumCost));

        // logic for ePPC and ePPA

        double wt_eppc = sumRevenue/sumClicks;
        double wt_eppa = sumRevenue/sumConversions;

        rootnode.attribs.put("ePPC", Double.toString(wt_eppc));
        rootnode.attribs.put("ePPA",Double.toString(wt_eppa));

        // logic for AvgBidValue
        double avgbidvalue = 0;
        for(TreeNode node : rootnode.children)
        {
            avgbidvalue += Double.parseDouble(node.attribs.get("NonZeroBid"))*Double.parseDouble(node.attribs.get("Avg Bid Value"));
        }

        rootnode.attribs.put("Avg Bid Value", Double.toString(avgbidvalue));

    }

    private static void getCosts() {
        costcsvfile = "/home/sumitkhanna/Desktop/Desktop/Work/DecilingCascade/test/cost.csv";

        try {

            String costLine;

            costSaikuReader = new BufferedReader(new FileReader(costcsvfile));

            while ((costLine = costSaikuReader.readLine()) != null) {
                String[] costColumns = costLine.split(",");
                String campaign = costColumns[0];
                String paytype = costColumns[1];
                String publisher = costColumns[2];
                String experiment = costColumns[3];
                String impressions = costColumns[4];
                String clicks = costColumns[5];
                String conversions = costColumns[6];
                String conversionsOneDay = costColumns[7];
                String revenue = costColumns[8];
                String cost = costColumns[9];
                String eppc = costColumns[10];
                String eppa = costColumns[11];

                // assumptions:-
                // form platform e.g web/app/fb from publisher
                // append publ | plat | adv as a branch
                // cpc -> ctr & cpa -> cvr
                // inserting in the same tree.

                String platform = null;
                String lastThree = publisher.length() <= 3 ? publisher : publisher.substring(publisher.length() - 3);
                ArrayList<String> branch = new ArrayList<String>();

                if(publisher.equalsIgnoreCase("null"))
                {
                    publisher = null;
                    platform = null;
                }
                else if(publisher.contains("FB"))
                {
                    platform = "FB";
                }
                else if(lastThree.equalsIgnoreCase("App"))
                {
                    platform = "APP";
                }
                else
                {
                    platform = "WEB";
                }

                if(publisher!=null)
                {
                    branch.add(publisher);
                }
                if(platform!=null)
                {
                    branch.add(platform);
                }
                if(campaign!=null)
                {
                    branch.add(campaign);
                }
                HashMap<String , String> keyVals = new HashMap<String,String>();
                keyVals.put("impressions", impressions);
                keyVals.put("clicks",clicks);
                keyVals.put("conversions", conversions);
                keyVals.put("conversionsOneDay", conversionsOneDay);
                keyVals.put("revenue", revenue);
                keyVals.put("cost", cost);
                keyVals.put("eppc", eppc);
                keyVals.put("eppa", eppa);
                keyVals.put("payoutType", paytype);
                insertBranchMap(root,branch,keyVals);
            }

        } catch (IOException e) {
            System.out.println("[EXCEPTION]Could not read the costs csv file");
        } finally {
            try {
                if (costSaikuReader != null)costSaikuReader.close();
            } catch (IOException ex) {
                System.out.println("[EXCEPTION]Could not close the costs csv file reader");
            }
        }
    }

    private static void getBids() {
        bidscsvfile = "/home/sumitkhanna/Desktop/Desktop/Work/DecilingCascade/test/bids.csv";
        try {

            String bidLine;

            bidsSaikuReader = new BufferedReader(new FileReader(bidscsvfile));

            while ((bidLine = bidsSaikuReader.readLine()) != null) {
                String[] bidCols = bidLine.split(",");
                String campaign = bidCols[0];
                String publisher = bidCols[1];
                String experiment = bidCols[2];
                String NZbid = bidCols[3];
                String Zbid = bidCols[4];
                String impressions = bidCols[5];
                String avgbidval = bidCols[6];

                // assumptions:-
                // form platform e.g web/app/fb from publisher
                // append publ | plat | adv as a branch
                // cpc -> ctr & cpa -> cvr
                // inserting in the same tree.

                String platform = null;
                String lastThree = publisher.length() <= 3 ? publisher : publisher.substring(publisher.length() - 3);
                ArrayList<String> branch = new ArrayList<String>();

                if(publisher.equalsIgnoreCase("null"))
                {
                    publisher = null;
                    platform = null;
                }
                else if(publisher.contains("FB"))
                {
                    platform = "FB";
                }
                else if(lastThree.equalsIgnoreCase("App"))
                {
                    platform = "APP";
                }
                else
                {
                    platform = "WEB";
                }

                if(publisher!=null)
                {
                    branch.add(publisher);
                }
                if(platform!=null)
                {
                    branch.add(platform);
                }
                if(campaign!=null)
                {
                    branch.add(campaign);
                }
                HashMap<String , String> keyVals = new HashMap<String,String>();
                keyVals.put("impressions", impressions);
                keyVals.put("NonZeroBid", NZbid);
                keyVals.put("ZeroBid", Zbid);
                keyVals.put("Avg Bid Value", avgbidval);
                insertBranchMap(root,branch,keyVals);
            }

        } catch (IOException e) {
            System.out.println("[EXCEPTION]Could not read the bids csv file");
        } finally {
            try {
                if (bidsSaikuReader != null)bidsSaikuReader.close();
            } catch (IOException ex) {
                System.out.println("[EXCEPTION]Could not close the bids csv file reader");
            }
        }

    }

    private static void buildTree() {
        root = new TreeNode("DEFAULT");
        for (Map.Entry<String, String> entry : decileMap.entrySet())
        {
            String branch = entry.getKey();
            String[] KV = branch.split("_A23_");
            String K = KV[0];
            String V = KV[1];

            String[] Nodes = K.split("_");
            ArrayList<String> nodeList = new ArrayList<String>(Arrays.asList(Nodes));

            insertBranch(root,nodeList,V,entry.getValue());
        }
    }

    private static void insertBranchMap(TreeNode root2,
            ArrayList<String> branch, HashMap<String, String> keyVals) {
        TreeNode rootCrawl = root;
        for(String node : branch)
        {
            if(existsNode(rootCrawl,node)!=-1)
            {
                int pos = existsNode(rootCrawl, node);
                rootCrawl = rootCrawl.children.get(pos);
            }
            else
            {
                TreeNode tree = new TreeNode(node);
                rootCrawl.children.add(rootCrawl.curr,tree);
                rootCrawl.curr++;
                rootCrawl = rootCrawl.children.get(rootCrawl.curr-1);
            }
        }
        for(Map.Entry<String, String> e : keyVals.entrySet())
        {
            rootCrawl.attribs.put(e.getKey(),e.getValue());
        }
    }

    // insert the key in the tree
    private static void insertBranch(TreeNode root, ArrayList<String> nodeList,
            String v, String value) {
        TreeNode rootCrawl = root;
        for(String node : nodeList)
        {
            if(existsNode(rootCrawl,node)!=-1)
            {
                int pos = existsNode(rootCrawl,node);
                rootCrawl = rootCrawl.children.get(pos);
            }
            else
            {
                TreeNode tree = new TreeNode(node);
                rootCrawl.children.add(rootCrawl.curr, tree);
                rootCrawl.curr++;
                rootCrawl = rootCrawl.children.get(rootCrawl.curr-1);
            }
        }
        rootCrawl.attribs.put(v, value);
    }

    // returns the position of TreeNode "node" in children of rootCrawl, -1 otherwise
    private static int existsNode(TreeNode rootCrawl, String node) {
        int pos = -1;
        int index = 0;
        for(TreeNode tn : rootCrawl.children)
        {
            if(tn.identifierLvl.equalsIgnoreCase(node))
            {
                return index;
            }
            else index++;
        }
        return pos;
    }

    private static void buildInfoMap() {
        decilefile = "/home/sumitkhanna/Desktop/Desktop/Work/DecilingCascade/test/intellibid-decile.ini"; // hardcoded - pass as args
        advInfoFile = "/home/sumitkhanna/Desktop/Desktop/Work/DecilingCascade/test/auto-const-conf.ini"; // hardcoded - pass as args

        try {
            String decileLn;// read the decileInfos file
            int header = 0;
            decileMaps mapToFill = null; // choose the Map to populate
            decileReader = new BufferedReader(new FileReader(decilefile));
            while ((decileLn = decileReader.readLine()) != null) {
                header ++; // an auxiliary variable
                if(header==1)
                {
                    mapToFill = decileMaps.advidsMap;
                }
                else if(header==3)
                {
                    mapToFill = decileMaps.decileMap;
                }
                else
                {
                    String[] splits = new String[2];
                    String key = null;
                    String value = null;

                    switch(mapToFill)
                    {
                    case advidsMap:
                        splits = decileLn.split("=");
                        key = splits[0];
                        value = splits[1];
                        String[] advids = value.split(",");
                        ArrayList<String> advidsList = new ArrayList<>(Arrays.asList(advids));
                        advidsMap.put(key, advidsList);
                        break;
                    case decileMap:
                        splits = decileLn.split("=");
                        key = splits[0];
                        value = splits[1];
                        decileMap.put(key, value);
                        break;
                    default:
                        break;
                    }
                }
            }
        } catch (IOException e) {
            System.out.println("[EXCEPTION]Problems reading decilefile");
        } finally {
            try {
                if (decileReader != null)decileReader.close();
            } catch (IOException ex) {
                System.out.println("[EXCEPTION]Problems closing decilefile");
            }
        }
        try {
            String advLn;// read the decileInfos file
            int header = 0;
            advInfoReader = new BufferedReader(new FileReader(advInfoFile));
            while ((advLn = advInfoReader.readLine()) != null) {
                header ++; // an auxiliary variable
                if(header==1)
                {
                    // skip
                }
                else
                {
                    String[] splits = advLn.split("=");
                    String key = splits[0];
                    String value = splits[1];
                    HashMap<String, String> innerAdvMap = createMapKV(value);
                    advInfoMap.put(key,innerAdvMap);
                }
            }
        } catch (IOException e) {
            System.out.println("[EXCEPTION]Problems reading advInfofile");
        } finally {
            try {
                if (decileReader != null)advInfoReader.close();
            } catch (IOException ex) {
                System.out.println("[EXCEPTION]Problems closing advInfofile");
            }
        }
    }

    private static HashMap<String, String> createMapKV(String value) {
        HashMap<String,String> MapKV = new HashMap<String,String>();
        value = value.substring(1);
        value = value.substring(0,value.length()-1);
        String[] valuesKV = value.split(",");
        ArrayList<String> KVPairs = new ArrayList<>(Arrays.asList(valuesKV));
        for(String KVstr : KVPairs)
        {
            String[] KsVs = KVstr.split(":");
            String K = KsVs[0];
            K = K.substring(1);
            K = K.substring(0,K.length()-1);
            String V = KsVs[1];
            V = V.substring(1);
            V = V.substring(0,V.length()-1);
            MapKV.put(K, V);
        }
        return MapKV;
    }

}
