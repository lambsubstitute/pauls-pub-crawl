@tool
extends "9_verb_inventory_grid.gd"


# Godot 4.7 auto-renames sibling nodes that share a name, so only the first slot keeps the exact
# EMPTY_SLOT name and every later item reports "No empty slot". Pick the first slot that holds no
# inventory item instead of matching on the name.
func _find_first_empty_slot() -> Control:
	for slot: Control in box.get_children():
		if not slot.get_children().any(func(c): return c is PopochiuInventoryItem):
			return slot
	return null
