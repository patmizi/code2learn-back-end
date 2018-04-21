# Todo: Match tag(event) with personality
import numpy as np

# personality dict from user (Extroversion, Emotional stability, Agreeableness, Conscientiousness, Interllect/Imagination
trait = { 
    "category_1": 13,
    "category_2": 1,
    "category_3": 67,
    "category_4": 34,
    "category_5": 67
}

# event dict from event
event1_tag = {
    "drinking": [1, 0, 1, 1, 1],
    "eating":   [1, 0, 1, 0, 0],
    "coding":   [0, 1, 0, 1, 1],
    "gaming":   [0, 1, 0, 0, 1],
    "sporting": [1, 0, 1, 0, 0]
}

event2_tag = {
    "drinking": [1, 0, 1, 1, 1],
    "eating":   [1, 0, 1, 0, 0],
    "coding":   [0, 1, 0, 1, 1],
    "dancing":  [0, 1, 0, 0, 1],
    "sporting": [1, 0, 1, 0, 0]
}
print(event1_tag.values())
#print(list(event1_tag.values())[0][0])
#print("Length : %d" % len (event1_tag))



# 5 tags max 
# combination of event points
# add each element of the array together (create sum-event-point)

# tag_matix = [
#     list(event1_tag.values())[0],
#     list(event1_tag.values())[1],
#     list(event1_tag.values())[2],
#     list(event1_tag.values())[3],
#     list(event1_tag.values())[4]
# ]
# print(np.matrix(tag_matix))

def main():
    # appending events
    tag_matrix = []
    for i in range(len(event2_tag)):
        tag_matrix.append(list(event2_tag.values())[i])
    print("Event matrix: \n", np.matrix(tag_matrix))

    trait_matrix = [
        list(trait.values())
    ]
    print("Trait matrix: ", np.matrix(trait_matrix))

    # TO BE MOD: call calculate_match function 
    calcedMatch = calculate_match("589765348967458967459867", tag_matrix, trait_matrix)
    print("Calculated match: ", calcedMatch)

    # TO BE MOD: call filter_match function
    filteredMatch = filter_match(calcedMatch)
    print("Filtered match: ", filteredMatch)
    #print("Filtered match: ", filtered_dict.update(calcedMatch))

# match calculation funtion - return dictionary of event and their perc differences
def calculate_match(eventID, tag_matrix, trait_matrix):
    # add each element of array in the dictionary vertically
    event_sum = np.matrix(tag_matrix).sum(axis=0)
    #print(event_sum)

    # calculate percentage of event
    perc_event = event_sum/len(event1_tag)
    #print("Event: ", perc_event)

    # calculate percentage of person trait
    perc_trait = np.matrix(trait_matrix)/100
    #print("Person: ", perc_trait)

    # calculate trait percentage differences between event and person
    perc_diff = abs(np.subtract(perc_event, perc_trait))
    #print("Diff: ", perc_diff)
    
    # convert matrix to array 
    #conv_diff = np.squeeze(np.asarray(perc_diff))

    # dictionary with eventID and the calculated percentage of difference between personality and event
    perc_avrg = np.average(perc_diff)

    calced_dict = {eventID: perc_avrg} 
    
    return calced_dict

# filter function - append element to dictionary
def filter_match(calculatedMatch):
    filtered_dict = {
        #sample values
        '679765348967458967459863':  0.4, #([[0.50, 0.60, 0.17, 0.46, 0.27]])
        '189765348967458967459864': 0.126 #([[0.37, 0.23, 0.01, 0.01, 0.01]]) 
    }
    ordered_dict = {}
    # append the new key-value pair
    filtered_dict.update(calculatedMatch)

    # sort the filtered dictionary base on values
    #sorted_dict = sorted(filtered_dict.values())
    for key, value in sorted(filtered_dict.items()):
        ordered_dict.update({key: value})
    return ordered_dict    
    #return sorted_dict





if __name__ == "__main__":
    main()



######## NOTES ############
# compare sum_event_point to perosnality?
## if personality score is over 50 then add them into the interest
## if 4 personility scores are lower than 50 pick the top 2  

## compare the sum_event_point array
## match? how do I match the top 