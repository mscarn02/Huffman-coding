#LIBRARY TO COMPRESS & DECOMPRESS A FILE USING HUFFMAN ENCODING ALGORITHM 

import heapq
import os

class HuffmanCoding:
	def __init__(self, path):
		self.path = path	#path to plaintext
		self.heap = []		#this is the priority queue
		self.codes = {}
		self.reverse_mapping = {}

	class HeapNode:
		def __init__(self, char, freq):
			self.char = char
			self.freq = freq
			self.left = None
			self.right = None

		# defining comparators less_than and equals
		def __lt__(self, other):
			return self.freq < other.freq

		def __eq__(self, other):
			if(other == None):	
				return False
			
			if(not isinstance(other, HeapNode)):
				return False
			return self.freq == other.freq

	# functions for compression:

	def make_frequency_dict(self, text):	#text is the stripped plaintext
		frequency = {}	#frequency dictionary
		#iterating over each character in text and counting the frequency of the character
		for character in text:	
			if not character in frequency:	#if the character is not in the frequency table, initialize it with the value 0
				frequency[character] = 0
			frequency[character] += 1	#if found, increase the frequency by 1

		return frequency

	#creates a priority queue
	def make_heap(self, frequency):	#frequency is the frequency table
		#iterate over each key (character) and make a node of [charcater, frequency]
		for key in frequency:
			node = self.HeapNode(key, frequency[key])	#creates the node
			heapq.heappush(self.heap, node)		#push the node into the heap made 

	def merge_nodes(self):
		while(len(self.heap)>1):	#do unitil there is only one element remaining in the PQ
			node1 = heapq.heappop(self.heap)	#pop the least valued node and store in node1
			node2 = heapq.heappop(self.heap)	#pop the second least valued node and sstore in node2

			merged = self.HeapNode(None, node1.freq + node2.freq)	#add the frequency of node 1 and nnode 2 and store in merged
			#make the merged node the parent of node 1 and node 2
			merged.left = node1	
			merged.right = node2

			heapq.heappush(self.heap, merged)	#push the merged node in heap


	def make_codes_helper(self, root, current_code):
		if(root == None):	#recursion has reached the leaf node
			return

		if(root.char != None):	#if the character is not none
			self.codes[root.char] = current_code
			self.reverse_mapping[current_code] = root.char
			return

		self.make_codes_helper(root.left, current_code + "0")
		self.make_codes_helper(root.right, current_code + "1")

	#this function initializes the huffman tree
	def make_codes(self):
		root = heapq.heappop(self.heap)	#takes the first element from PQ to be the root
		current_code = ""
		self.make_codes_helper(root, current_code)

	def get_encoded_text(self, text):

		encoded_text = ""
		for character in text:
			encoded_text += self.codes[character]
		return encoded_text

	def pad_encoded_text(self, encoded_text):

		extra_padding = 8 - len(encoded_text) % 8	#checks how many extra '0''s are needed
		for i in range(extra_padding):
			encoded_text += "0"		#adds that many zeroes

		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text

	def get_byte_array(self, padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		for i in range(0, len(padded_encoded_text), 8):
			byte = padded_encoded_text[i:i+8]
			b.append(int(byte, 2))
		return b

	def compress(self):
		filename, file_extension = os.path.splitext(self.path)	#splitext returns the name_of_file + extension as a tuple
		output_path = filename + ".bin"	#extension of output file is .bin

		with open(self.path, 'r') as file, open(output_path, 'wb') as output:	#opens the path in reading mode as file, opens the output_path in write binary mode
			text = file.read()	#reads the file data in text variable
			text = text.rstrip()	#strips the text of spaces

			frequency = self.make_frequency_dict(text)	#frequency stores the frequency table
			self.make_heap(frequency)	#heap (priority queue) made
			self.merge_nodes()	#merges the two least nodes
			self.make_codes()	#makes codes 

			encoded_text = self.get_encoded_text(text)	#encoded text contains the encoded text
			padded_encoded_text = self.pad_encoded_text(encoded_text)

			b = self.get_byte_array(padded_encoded_text)
			output.write(bytes(b))

		print("Compressed")
		return output_path

	""" functions for decompression: """

	def remove_padding(self, padded_encoded_text):
		padded_info = padded_encoded_text[:8]
		extra_padding = int(padded_info, 2)

		padded_encoded_text = padded_encoded_text[8:] 
		encoded_text = padded_encoded_text[:-1*extra_padding]

		return encoded_text

	def decode_text(self, encoded_text):
		current_code = ""
		decoded_text = ""

		for bit in encoded_text:
			current_code += bit
			if(current_code in self.reverse_mapping):
				character = self.reverse_mapping[current_code]
				decoded_text += character
				current_code = ""

		return decoded_text

	def decompress(self, input_path):
		filename, file_extension = os.path.splitext(self.path)
		output_path = filename + "_decompressed" + ".txt"

		with open(input_path, 'rb') as file, open(output_path, 'w') as output:
			bit_string = ""

			byte = file.read(1)
			while(len(byte) > 0):
				byte = ord(byte)
				bits = bin(byte)[2:].rjust(8, '0')
				bit_string += bits
				byte = file.read(1)

			encoded_text = self.remove_padding(bit_string)

			decompressed_text = self.decode_text(encoded_text)
			
			output.write(decompressed_text)

		print("Decompressed")
		return output_path
