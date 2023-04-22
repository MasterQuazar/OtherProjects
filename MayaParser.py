import os
import pickle
from termcolor import *
import colorama

colorama.init()


def parse_ascii_file_function(filepath):
	#filepath = "C:/Users/metal/Desktop/mayatest.ma"
	#filepath = "D:/WORK/LIGHTING/FISHNEEDSFIRE/maya/scenes/char_grooming_MainScene_v004.ma"
	nodes_index = {}
	nodes_number = 0 
	document_starting_line = []
	lines = []
	connection_list = []

	node_data = {}

	"""
	FIRST PARSING LOOP
		gets all nodes created in the file
		gets the main attributes of those nodes (name, type, parents, shared)
		gets the index in the file
	"""
	with open(filepath, "r") as read_file:
		for i, line in enumerate(read_file):
			lines.append(line)
			if line.startswith("\t") == False:
				document_starting_line.append(i+1)
			if line.startswith("createNode"):

				splited_node_line = line.split(" ")
				#print(splited_node_line)

				#PARSE THE CREATE NODE LINE
				node_type = splited_node_line[1]
				node_name = None 
				node_parent = None 

				if ("-n" in splited_node_line):
					node_name = (splited_node_line[splited_node_line.index("-n") + 1].translate({ord(y):None for y in '";'})).rstrip()
				if ("-p" in splited_node_line):
					node_parent = splited_node_line[splited_node_line.index("-p") + 1]

				#create node dictionnary

				
				node_data = {
					"nodeCommand":"create",
					"nodeType":node_type,
					"nodeParent":node_parent,
					"nodeShared":("-s" in splited_node_line),
					"nodeIndexInFile":i+1,
					"nodeUid":None
				}

				nodes_index[node_name] = node_data

			elif line.startswith("connectAttr"):
				splited_line = line[:-1].replace('"', '').replace(";", "").split(" ")
				
				if ("-na" in splited_line)==True:
					next_value=True
				else:
					next_value=False
				
				connection_origin = splited_line[1]
				connection_destination = splited_line[2]

				connection_list.append([connection_origin, connection_destination, next_value])

			elif line.startswith("relationship"):
				splited_line = line[:-1].replace('"', '').replace(";", "").split(" ")
				splited_line.pop(0)
				relation_list = splited_line


			#PUT NO EXPAND ON TRUE WHILE SELECTING (TRUE FOR ALL ITEMS)
			elif line.startswith("select"):
				node_name = line[:-1].split(" ")[-1]
				node_name = node_name[:-1]

				node_data = {
					"nodeCommand":"select",
					"nodeType":None,
					"nodeParent":None,
					"nodeShared":None,
					"nodeIndexInFile":i+1,
					"nodeUid":None
				}
				nodes_index[node_name] = node_data


			else:
				continue




	nodes_index_keys = list(nodes_index.keys())

	for i, node_name in enumerate(nodes_index_keys):
		attribute_dictionnary = {}
		set_attribute_dictionnary = {}
		add_attribute_dictionnary = {}
		node_data = nodes_index[node_name]
		node_data["nodesGlobalAttributes"] = {}
		node_data["nodesSetAttributes"] = {}
		node_data["nodesAddAttributes"] = {}


		if node_data["nodeCommand"]=="create":
			#keyable value by default is true!!
			node_data["nodeKeyable"] = "on"
			#check new lines
			starting_line = node_data["nodeIndexInFile"]
			ending_line = document_starting_line[document_starting_line.index(starting_line)+1]

			"""
			print(colored("CHECKING NODE [%s] ##############################################################################"%node_name, "red"))
			print(colored("\tnode attribute range [%s ; %s]"%(starting_line, ending_line), "red"))
			"""

			for i in range(starting_line, ending_line):
				splited_line = lines[i].strip().split(" ")
				if (splited_line[0] == "rename") and (splited_line[1] == "-uid"):
					node_data["nodeUid"] = splited_line[2].replace(";", "")

				if (splited_line[0] == "setAttr"):
					#print(splited_line)
					
					#attribute_name = None 
					if "-k" in splited_line:
						#print(colored("KEYABLE KEYWORD", "cyan"))
						keyable = splited_line.index("-k")
						node_data["nodeKeyable"] = "off"

						attribute_name = splited_line[3].replace('"', '')
						index = 3
					else:
						attribute_name = splited_line[1].replace('"', '')
						index = 1
					#print(node_data["nodeKeyable"])

					#print("\t%s"%index)


					attribute_name = attribute_name.replace('.', '')
					try:
						if splited_line[index + 1] == "-type": 
							attribute_dictionnary[attribute_name] = " ".join(splited_line[int(index + 3):])
						else:
							attribute_dictionnary[attribute_name] = splited_line[index + 1]
					except:
						print("[Line %s] - no more values found"%i)
						pass
			node_data["nodesGlobalAttributes"] = attribute_dictionnary



		if node_data["nodeCommand"]=="select":
			starting_line = node_data["nodeIndexInFile"]
			ending_line = document_starting_line[document_starting_line.index(starting_line) + 1]

			for i in range(starting_line, ending_line):
				splited_line = (lines[i])[:-1].replace('"', '').replace(';', '').strip().split(" ")
				#print(i, splited_line)

				node_data["nodeSelectSize"] = None
				if (splited_line[0] == "setAttr"):
					if ("-s" in splited_line):
						size = splited_line[splited_line.index("-s") + 1]
						attribute_name = splited_line[splited_line.index("-s") + 2]
						attribute_value = None
					else:
						size = None
						attribute_name = splited_line[1]
						attribute_value = splited_line[2]

					if ("-type" in splited_line):
						attribute_value = splited_line[splited_line.index("-type") + 2]
						attribute_name = splited_line[1]
						size = None

					set_attribute_dictionnary[attribute_name] = [size, attribute_value]

				if (splited_line[0] == "addAttr"):
					ci_value = False
					hidden_value = False
					longname_value = None
					shortname_value = None 
					datatype_value = None

					if ("-ci" in splited_line):
						ci_value = splited_line[splited_line.index("-ci") + 1]
					if ("-h" in splited_line):
						hidden_value = splited_line[splited_line.index("-h") + 1]
					if ("-ln" in splited_line):
						longname_value = splited_line[splited_line.index("-ln") + 1]
					if ("-sn" in splited_line):
						shortname_value = splited_line[splited_line.index("-sn") + 1]
					else:
						shortname_value = longname_value
					if ("-dt" in splited_line):
						datatype_value = splited_line[splited_line.index("-dt") + 1]

					add_attribute_dictionnary[longname_value] = {
						"ciValue": ci_value,
						"hiddenValue": hidden_value,
						"longNameValue": longname_value,
						"shortNameValue": shortname_value,
						"dataTypeValue":datatype_value
					}
			node_data["nodesSetAttributes"] = set_attribute_dictionnary
			node_data["nodesAddAttributes"] = add_attribute_dictionnary



	#DISPLAY VALUES WITH TERMCOLOR
	"""	
	for node, node_value in nodes_index.items():
		print(colored("-------------------------------\n%s"%node, "red"))

		for item, item_values in node_value.items():
			print(colored("----%s"%item,"green"))
			if type(item_values) == dict:
				for key, value in item_values.items():
					print(key, value)
			else:
				print(item_values)
						
			

	print(colored("########## RELATIONS ##########", "magenta"))
	for items in relation_list:
		print(items)

	print(colored("########## CONNECTIONS ##########", "magenta"))
	for item in connection_list:
		print(item)
	
	return nodes_index, connection_list, relation_list
	"""
	
#parse_ascii_file_function("test")






	
	



