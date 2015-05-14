import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class decileTreeBuilder {
	private static String decilefile;// filename for intellibid-decile.ini
	private static String advInfoFile;// filename for auto-const-conf.ini

	private static BufferedReader decileReader = null;// reads the intellibid-decile.ini
	private static BufferedReader advInfoReader = null;//reads the auto-const-conf.ini

	private static HashMap<String, String> decileMap = new HashMap<String,String>();//storing decile weights/cutoffs
	private static HashMap<String, ArrayList<String>> advidsMap = new HashMap<String,ArrayList<String>>();//storing advids list

	private static HashMap<String, HashMap<String,String>> advInfoMap = new HashMap<String,HashMap<String,String>>();
	
	enum decileMaps { advidsMap,decileMap };// flip-flop to chose the map

	public static void main(String[] args) { // main function
		buildInfoMap(); // populate the files - decilefile & advInfoFile
		
		//Now that we have read the weights and advInfo files :- 
		//Let us costruct the tree .1
		//And stick data onto it   .2
		
		buildTree(); // the tree has been built, the stage has been set
		
		
		
		
	}

	private static void buildTree() {
		TreeNode root = new TreeNode("DEFAULT");
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
		decilefile = "intellibid-decile.ini"; // hardcoded - pass as args
		advInfoFile = "auto-const-conf.ini"; // hardcoded - pass as args

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
			System.out.println("Problems reading decilefile");
		} finally {
			try {
				if (decileReader != null)decileReader.close();
			} catch (IOException ex) {
				System.out.println("Problems closing decilefile");
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
			System.out.println("Problems reading advInfofile");
		} finally {
			try {
				if (decileReader != null)advInfoReader.close();
			} catch (IOException ex) {
				System.out.println("Problems closing advInfofile");
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
