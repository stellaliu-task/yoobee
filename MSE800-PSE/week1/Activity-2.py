import numpy as np
arr = np.arange(1,11)
print(arr)
print('shape:', arr.shape)
print('data type:', arr.dtype)
print('multiplied by 2:', arr * 2)
print('\n')

scores = np.array([
    [78, 85, 90],
    [88, 79, 92],
    [84, 76, 88],
    [90, 93, 94],
    [75, 80, 70]
])
print('Average scores for each student:', scores.mean(axis=1))
print('Average scores for each subject:', scores.mean(axis=0))

temp_arr = scores.sum(axis=1)
print('The student with the highest total score:', np.argmax(temp_arr)+1)

scores[:, 2] = scores[:, 2]+5
print('After added 5 bonus points:', scores)