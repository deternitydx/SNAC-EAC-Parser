import java.io.File;
import java.io.FilenameFilter;
import java.util.HashMap;
import java.util.Map;

import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;
import org.neo4j.graphdb.Node;

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
	
	public Parser(String gdb, String eac) {
		graphDbLocation = gdb;
		eacLocation = eac;
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
		graphDb = new GraphDatabaseFactory()
		    .newEmbeddedDatabaseBuilder( graphDbLocation )
		    .setConfig( config )
		    .newGraphDatabase();
		
		// This would open an existing DB
		//graphDb = new GraphDatabaseFactory().newEmbeddedDatabase( graphDbLocation );
		
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
				
				Node v = graphDb.createNode();

				tx.success();
			}
			finally {
				tx.close();
			}
		}
		
	}

}
