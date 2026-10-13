from huff816_table_probe import table

def prefix_free(entries):
 return all(not (a[0]<z[0] and a[1]==z[1]>>(z[0]-a[0])) for a in entries for z in entries)
