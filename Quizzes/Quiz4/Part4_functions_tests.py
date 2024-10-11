import unittest
from Part4_functions import valence
import dis
import requests

# Testing the functions file specifically - slightly different function form than I used in the mapper

class TestValence(unittest.TestCase):
    def test_normal(self):
        '''
        A typical sequence of three words
        '''
        self.assertEqual(valence('yeah winner worst'),[1, 4, -3])

    def test_empty(self):
        '''
        Empty string input
        '''
        self.assertEqual(valence(''),[])

    def test_nonword(self):
        '''
        Words not in afinn dictionary should be skipped
        '''
        self.assertEqual(valence('qqqqqq'),[])

    def test_quotes(self):
        '''
        Words in quotes should still parse correctly
        '''
        self.assertEqual(valence('"yeah" "winner worst"'),[1, 4, -3])

    def test_seperators(self):
        '''
        Testing that various seperators are removed, and special characters ignored
        '''
        self.assertEqual(valence('yeah\twinner\tworst'),[1, 4, -3])
        self.assertEqual(valence('yeah\t\twinner\t\tworst'),[1, 4, -3])
        self.assertEqual(valence('yeah\nwinner\nworst\t\n'),[1, 4, -3])
        self.assertEqual(valence('yeah! *winner[\n]worst$%^&'),[1, 4, -3])
    
    def test_nonprintable(self):
        '''
        Only nonprintable characters are removed
        '''
        self.assertEqual(valence('\n'),[])
        self.assertEqual(valence('\n*@$%&($\n'),[])

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
        self.assertEqual(valence(bc_string),[2, 2])

    def test_bytestring(self):
        '''
        Byte strings should be decoded first
        '''
        self.assertEqual(valence(b'yeah winner worst'),[1, 4, -3])

if __name__ == '__main__':
    unittest.main()