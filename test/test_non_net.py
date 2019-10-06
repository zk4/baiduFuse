

# part_size = 3
# def test_get_block_range(offset,size):
#     start_idx = offset // part_size
#     end_idx = (size + offset) // part_size
#     return [start_idx,end_idx]


# ret= test_get_block_range(2,3)
# print(ret)
totoal_size = 55536
part_size = 1000
def get_block_range(offset,size):
    start_idx = offset // part_size 
    end_idx = (size + offset) // part_size
    return [start_idx,end_idx]


for i in range(*get_block_range(10,20)):
    print(i)

