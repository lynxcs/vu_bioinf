from ete3 import Tree

t = Tree('tree.txt')

t.set_outgroup("lcl|Query_41789664901-8458_MN514967.1_Dromedary_camel_coronavirus_HKU23_isolate_DcCoV-HKU23/camel/Nigeria/NV1385/2016")

t.write(outfile='tree2.txt')