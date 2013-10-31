import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;


// Graph Libraries
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;
import org.neo4j.graphdb.Node;

// XML Libraries
import org.w3c.dom.Document;
import org.xml.sax.SAXException;
import org.w3c.dom.NamedNodeMap;
//import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import com.sun.org.apache.xerces.internal.parsers.DOMParser;

/**
 * 
 */

/**
 * @author Robbie Hott
 *
 */
public class Parser {

	private GraphDatabaseService graphDb;
	private String graphDbLocation;
	private String eacLocation;
	private DOMParser dp;
	private Document doc;
	
	public Parser(String gdb, String eac) {
		graphDbLocation = gdb;
		eacLocation = eac;
		dp = new DOMParser();
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Parser p = new Parser(args[0], args[1]);
		p.parse();

	}
	
	private static void registerShutdownHook( final GraphDatabaseService graphDb )
	{
	    // Registers a shutdown hook for the Neo4j instance so that it
	    // shuts down nicely when the VM exits (even if you "Ctrl-C" the
	    // running application).
	    Runtime.getRuntime().addShutdownHook( new Thread()
	    {
	        @Override
	        public void run()
	        {
	            graphDb.shutdown();
	        }
	    } );
	}


	public void parse() {
		// TODO Auto-generated method stub
		
		Map<String, String> config = new HashMap<String, String>();
		config.put( "neostore.nodestore.db.mapped_memory", "2048M" );
		//config.put( "string_block_size", "60" );
		//config.put( "array_block_size", "300" );
		
		// Create a new database
		//graphDb = new GraphDatabaseFactory()
		//    .newEmbeddedDatabaseBuilder( graphDbLocation )
		//    .setConfig( config )
		//    .newGraphDatabase();
		
		// Create a new database
		graphDb = new GraphDatabaseFactory().newEmbeddedDatabase( graphDbLocation );
		
		// Register shutdown hook in case this dies
		registerShutdownHook( graphDb );
		
		// Open the eac directory
		File eacDir = new File(eacLocation);
		if (!eacDir.isDirectory()) {
			System.err.println("Could not read EAC Directory.");
			System.exit(1);
		}
		
		// for each item in the directory, read and parse the eac record,
		// then update the graph database (in a transaction)
		for (File f : eacDir.listFiles()) {
			// Start a transaction
			Transaction tx = graphDb.beginTx();
			try {
				// Read the file and update the graph
				// ...
				
				dp.parse(f.getAbsolutePath());
				doc = dp.getDocument();
				NodeList root = doc.getChildNodes();
				

				Node v = graphDb.createNode();
				
				NodeList cpfDescription = getNode("cpfDescription", root).getChildNodes();
				NodeList identity = getNode("identity", cpfDescription).getChildNodes();
				v.setProperty("entityType", getNodeValue(getNode("entityType",identity)));
				v.setProperty("identity", getNodeValue(getNode("nameEntry", identity).getChildNodes().item(0)));
				v.setProperty("filename", f.getName());
				
				NodeList control = getNode("control", root).getChildNodes();
				HashSet<String> viaf = new HashSet<String>();
				HashSet<String> dbpedia = new HashSet<String>();
				HashSet<String> referencedIn = new HashSet<String>();
				HashSet<String> creatorOf = new HashSet<String>();
				String tmp;
				
				for (int i = 0; i < control.getLength(); i++) {
					if (control.item(i).getNodeName().equals("recordId"))
						v.setProperty("recordId", control.item(i).getNodeValue());
					if ((tmp = getNodeAttr("localType", control.item(i))).equals("VIAFId")) {
						// add to the viaf list
						viaf.add(tmp.replace("VIAFId:", "http://viaf.org/viaf/"));
					}
					if ((tmp = getNodeAttr("localType", control.item(i))).equals("dbpedia")) {
						// add to the viaf list
						dbpedia.add(tmp.replace("dbpedia:", ""));
					}
				}
				
				v.setProperty("viaf", viaf);
				v.setProperty("dbpedia", dbpedia);
				
				

				tx.success();
			} catch (SAXException e) {
				// TODO Auto-generated catch block
				System.err.println("Could not parse: " + f.getName());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.println("Could not read : " + f.getName());
			}
			finally {
				tx.close();
			}
		}
		
	}
	
	
	// Helper methods provided by:
	//
	
	protected org.w3c.dom.Node getNode(String tagName, NodeList nodes) {
	    for ( int x = 0; x < nodes.getLength(); x++ ) {
	        org.w3c.dom.Node node = nodes.item(x);
	        if (node.getNodeName().equalsIgnoreCase(tagName)) {
	            return node;
	        }
	    }
	 
	    return null;
	}
	 
	protected String getNodeValue( org.w3c.dom.Node node ) {
	    NodeList childNodes = node.getChildNodes();
	    for (int x = 0; x < childNodes.getLength(); x++ ) {
	        org.w3c.dom.Node data = childNodes.item(x);
	        if ( data.getNodeType() == org.w3c.dom.Node.TEXT_NODE )
	            return data.getNodeValue();
	    }
	    return "";
	}
	 
	protected String getNodeValue(String tagName, NodeList nodes ) {
	    for ( int x = 0; x < nodes.getLength(); x++ ) {
	        org.w3c.dom.Node node = nodes.item(x);
	        if (node.getNodeName().equalsIgnoreCase(tagName)) {
	            NodeList childNodes = node.getChildNodes();
	            for (int y = 0; y < childNodes.getLength(); y++ ) {
	                org.w3c.dom.Node data = childNodes.item(y);
	                if ( data.getNodeType() == org.w3c.dom.Node.TEXT_NODE )
	                    return data.getNodeValue();
	            }
	        }
	    }
	    return "";
	}
	 
	protected String getNodeAttr(String attrName, org.w3c.dom.Node node ) {
	    NamedNodeMap attrs = node.getAttributes();
	    for (int y = 0; y < attrs.getLength(); y++ ) {
	        org.w3c.dom.Node attr = attrs.item(y);
	        if (attr.getNodeName().equalsIgnoreCase(attrName)) {
	            return attr.getNodeValue();
	        }
	    }
	    return "";
	}
	 
	protected String getNodeAttr(String tagName, String attrName, NodeList nodes ) {
	    for ( int x = 0; x < nodes.getLength(); x++ ) {
	        org.w3c.dom.Node node = nodes.item(x);
	        if (node.getNodeName().equalsIgnoreCase(tagName)) {
	            NodeList childNodes = node.getChildNodes();
	            for (int y = 0; y < childNodes.getLength(); y++ ) {
	                org.w3c.dom.Node data = childNodes.item(y);
	                if ( data.getNodeType() == org.w3c.dom.Node.ATTRIBUTE_NODE ) {
	                    if ( data.getNodeName().equalsIgnoreCase(attrName) )
	                        return data.getNodeValue();
	                }
	            }
	        }
	    }
	 
	    return "";
	}

}
