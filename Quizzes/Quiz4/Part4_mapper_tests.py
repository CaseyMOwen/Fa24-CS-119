import unittest
from Part4_mapper import valence, get_afinn_dict
import dis
import requests

class TestValence(unittest.TestCase):
    def setUp(self):
        self.afinn_dict = get_afinn_dict()
        stopwords_list = requests.get("https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt").content
        self.stopwords = list(set(stopwords_list.splitlines()))

    def test_normal(self):
        '''
        A typical sequence of three words
        '''
        self.assertEqual(valence('yeah winner worst', self.afinn_dict, self.stopwords),[1, 4, -3])

    def test_empty(self):
        '''
        Empty string input
        '''
        self.assertEqual(valence('', self.afinn_dict, self.stopwords),[])

    def test_nonword(self):
        '''
        Words not in afinn dictionary should be skipped
        '''
        self.assertEqual(valence('qqqqqq', self.afinn_dict, self.stopwords),[])

    def test_quotes(self):
        '''
        Words in quotes should still parse correctly
        '''
        self.assertEqual(valence('"yeah" "winner worst"', self.afinn_dict, self.stopwords),[1, 4, -3])

    def test_seperators(self):
        '''
        Testing that various seperators are removed, and special characters ignored
        '''
        self.assertEqual(valence('yeah\twinner\tworst', self.afinn_dict, self.stopwords),[1, 4, -3])
        self.assertEqual(valence('yeah\t\twinner\t\tworst', self.afinn_dict, self.stopwords),[1, 4, -3])
        self.assertEqual(valence('yeah\nwinner\nworst\t\n', self.afinn_dict, self.stopwords),[1, 4, -3])
        self.assertEqual(valence('yeah! *winner[\n]worst$%^&', self.afinn_dict, self.stopwords),[1, 4, -3])
    
    def test_nonprintable(self):
        '''
        Only nonprintable characters are removed
        '''
        self.assertEqual(valence('\n', self.afinn_dict, self.stopwords),[])
        self.assertEqual(valence('\n*@$%&($\n', self.afinn_dict, self.stopwords),[])

    def ex_function():
        '''
        Function to get bytecode of in below test - clean and true both have valences of 2 - no other words in bytecode are present
        '''
        clean = True
    
    def test_bytecode_string(self):
        '''
        Bytecode string should interpret the given instructions
        '''
        bc_string = dis.Bytecode(self.ex_function).dis()
        self.assertEqual(valence(bc_string, self.afinn_dict, self.stopwords),[2, 2])

    def test_bytestring(self):
        '''
        Byte strings should be decoded first
        '''
        self.assertEqual(valence(b'yeah winner worst', self.afinn_dict, self.stopwords),[1, 4, -3])

if __name__ == '__main__':
    unittest.main()