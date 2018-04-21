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
tag_matix = [
    list(event1_tag.values())[0],
    list(event1_tag.values())[1],
    list(event1_tag.values())[2],
    list(event1_tag.values())[3],
    list(event1_tag.values())[4]
]
print(np.matrix(tag_matix))

trait_matrix = [
    list(trait.values())
]
print(np.matrix(trait_matrix))



# add the element of each event array in the dictionary
event_sum = np.matrix(tag_matix).sum(axis=0)
print(event_sum)

# calculate percentage of event
perc_event = event_sum/len(event1_tag)
print(perc_event)

# calculate percentage of person trait
perc_trait = np.matrix(trait_matrix)/100
print(perc_trait)

#calculate trait percentage differences between event and person
perc_diff = abs(np.subtract(perc_event, perc_trait))
print("Diff: ", perc_diff)



# compare sum_event_point to perosnality?
## if personality score is over 50 then add them into the interest
## if 4 personility scores are lower than 50 pick the top 2  

## compare the sum_event_point array
## match? how do I match the top 