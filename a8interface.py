#
# CS116, Winter 2011
# Assignment #8 (Module 8)
#

class SampleBlock:
    'Fields: samples, average_amplitude'
    # You do not need to worry about the following two defs (__init__ and __repr__), but
    # you should include them when copying the class definition to your own files

    # The following def serves to initialize the object to default values
    def __init__(self):
        "This initializes the SampleBlock object to default values"
        self.samples = []
        self.average_amplitude = 0.0
    # The following def will create a string representation of the object when you attempt
    # to print it. This is useful for debugging
    def __repr__(self):
        "The __repr__ method will return a string representation of this SampleBlock"
        return "samples: " + str(self.samples) + ", average_amplitude: " + str(self.average_amplitude)

#
# Question 1
#

def chop_samples(float_list, block_size):
    # Your code here (remove "pass" below when writing your code)
    pass


#
# Question 2
#

def sort_sample_blocks(sample_block_list):
    # Your code here (remove "pass" below when writing your code)
    pass


#
# Question 3
#

def find_closest_sample_block_index(target_sample_block, sorted_list_of_sample_blocks):
    # Your code here (remove "pass" below when writing your code)
    pass


#
# Question 4
#

def calculate_sum_square_difference(left_sample_block, right_sample_block):
    # Your code here (remove "pass" below when writing your code)
    pass


#
# Question 5
#

def find_best_match(target_sample_block,
                    list_of_replacement_sample_blocks,
                    similarity_function,
                    start_index,
                    num_neighbours):
    lower_bound = max(start_index-num_neighbours, 0)
    upper_bound = min(start_index+num_neighbours,
                      len(list_of_replacement_sample_blocks))