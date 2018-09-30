import java.io.*;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.*;
import java.io.BufferedReader;
import java.io.FileReader;

import edu.mit.jwi.Dictionary;
import edu.mit.jwi.item.*;

public class ExtractSocialActors{
	public static PrintWriter verboseWriter;
	public static PrintWriter writer;
	public static void main(String[] args) throws IOException {
		String WNdictionaryFolderPath = "WordNet-3.0" + File.separator + "dict";
		
   		URL url = new URL("file", null, WNdictionaryFolderPath);
   		
    	// construct the dictionary object and open it
    	Dictionary dict = new Dictionary(url);
		dict.open();
		Stack<IWordID> wordIDs = new Stack<IWordID>();
		/*
        for(IWordID bobID : dict.getIndexWord("",POS.NOUN).getWordIDs()){
        	IWord bob = dict.getWord(bobID);
	        ISynset synset = bob.getSynset();
	        System.out.println(synset.getGloss());
	        List<ISynsetID> hyponyms = 
				synset.getRelatedSynsets(Pointer.HYPONYM);
			for (ISynsetID sid: hyponyms){
				for(IWord hyponym: dict.getSynset(sid).getWords()){ 
					System.out.println(hyponym.getLemma());
				}
			}
        }
        */
        try{
   			verboseWriter = new PrintWriter("social-actor-list-verbose.txt");
			writer = new PrintWriter("social-actor-list.txt");
		}
		catch(FileNotFoundException e){
			System.out.println("Can not open file "+e.getMessage());
			return;
		}
		IIndexWord ppl = dict.getIndexWord("person",POS.NOUN);
		writer.println("person");
        IIndexWord org = dict.getIndexWord("social group",POS.NOUN);
        writer.println("organization");
        wordIDs.add(ppl.getWordIDs().get(0));
        wordIDs.add(org.getWordIDs().get(0));
        // Choose the words "people" and "organization" as starting points
        dfs(dict,wordIDs);

        verboseWriter.close();
        writer.close();
        /*
        IWordID[] wordIDs = ppl.getWordIDs();
        for(IWordID id: wordIDs){
        	System.out.println(id.getLemma()+": "+id.)
        }
        */


	}

	private static void dfs(Dictionary dict, Stack<IWordID> wordIDs){
		ArrayList<IWordID> visited = new ArrayList<IWordID>();
		while(!wordIDs.empty()){
			IWordID wordID = wordIDs.pop();
			ArrayList<IWordID> hyponyms = getHyponyms(dict, wordID, visited);
			wordIDs.addAll(hyponyms);
		}
	}

	public static ArrayList<IWordID> getHyponyms(Dictionary dict, IWordID wordID, ArrayList<IWordID> visited){
		IWord word = dict.getWord(wordID);
		ISynset synset = word.getSynset();
		List<ISynsetID> hyponyms = 
			synset.getRelatedSynsets(Pointer.HYPONYM);
		ArrayList<IWordID> wordIDs = new ArrayList<IWordID>(); // result IDs
		for (ISynsetID sid: hyponyms){
			for(IWord hyponym: dict.getSynset(sid).getWords()){ 
				// iterate through each wordID and check if it is a frequently used sense
				ISynsetID candidate = hyponym.getSynset().getID();
				IIndexWord idxWord = dict.getIndexWord(hyponym.getLemma(),POS.NOUN);
				
				int threshold = Math.min(idxWord.getWordIDs().size(),2);
				for(int i=0; i<threshold;i++){
					IWordID tmp = idxWord.getWordIDs().get(i);
					ISynsetID tmpID = tmp.getSynsetID();
					if (tmpID.getOffset() == candidate.getOffset()){
						if (!visited.contains(tmp)){
							//System.out.println("A match");
							//System.out.println("The sense of "+ hyponym.getLemma()+" :"+" "+hyponym.getSynset().getGloss());
							//System.out.println("This sense has a count of "+Integer.toString(idxWord.getTagSenseCount()));
							visited.add(tmp); // mark visited
							wordIDs.add(tmp);
							writer.println(tmp.getLemma());
							verboseWriter.println(tmp.getLemma());
							verboseWriter.println("The sense of "+ tmp.getLemma()+" :"+" "+dict.getWord(tmp).getSynset().getGloss());
							verboseWriter.println("This sense has a count of "+Integer.toString(idxWord.getTagSenseCount()));
							System.out.println("Writting: "+tmp.getLemma());
							System.out.println("Adding: "+tmp.getLemma()+"'s "+Integer.toString(i)+" th meaning");
						}
					}

				}

				
			}
		}
		return wordIDs;
	}
}