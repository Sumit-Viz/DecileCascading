import java.util.ArrayList;
import java.util.HashMap;


public class TreeNode {
	ArrayList<TreeNode> children;
	String identifierLvl;
	HashMap<String,String> attribs;
	int curr;
	
	public TreeNode(String level) {
		this.identifierLvl = level;
		this.curr = 0;
		children = new ArrayList<TreeNode>();
		attribs = new HashMap<String,String>();
	}
}
