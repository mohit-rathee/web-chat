mylist = [21, 5, 8, 52, 21, 87, 52]
item = 67

try:
	#search for the item
	index = mylist.index(item)
	print('The index of', item, 'in the list is:', index)
except ValueError:
	print('item not present')