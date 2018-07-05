def DetectCurrentFace( Group ):

    import scipy.io as scio
    import sys
    import numpy as np

### This was used for testing purposes only

    # import hebi  # for the Hebi motors
    # from time import sleep
    #
    # # Need to look into XML formatting for Hebi Gains
    # # sio.loadmat('defaultGains.mat')
    #
    # lookup = hebi.Lookup()  # Get table of all Hebi motors
    # sleep(2)  # gives the Lookup process time to discover modules
    # 
    # # Displays the Hebi modules found on the network
    # print('Modules found on the network:')
    #
    # for entry in lookup.entrylist:
    #     print('{0} | {1}'.format(entry.family, entry.name))
    #
    # # print('\n')
    #
    # var = raw_input('Were any modules found? [y/N]: \n')
    # if var == 'y':
    #     print('\nYay!\n')
    # elif var == 'Y':
    #     print('\nYay!\n')
    # else:
    #     print('\nNONE FOUND!\n')
    #     sys.exit()
    #
    # Group = lookup.get_group_from_family('*')
    # infoTable = Group.request_info()

### This was used for testing purposes only

    trainingData = scio.loadmat('IMUTrainingRutgers.mat') # training data gathered from MATLAB

    labels = np.float(trainingData['labs'][0][0][0])

    for i in range(1,len(trainingData['labs'])):
        labels = np.append(labels,np.float(trainingData['labs'][i][0][0]))

    # Create KNN model
    from sklearn.neighbors import KNeighborsRegressor
    knn = KNeighborsRegressor(n_neighbors=10)
    # Fit the model
    knn.fit(trainingData['trainingData'], labels)

    fbk = hebi.GroupFeedback(Group.size)
    Group.feedback_frequency = 200.0
    fbk = Group.get_next_feedback(reuse_fbk=fbk)

    # if(fbk.size != trainingData['nbMotors'][0][0]):
    #     print('Something is wrong with the number of connected motors!')
    #     return 0

    accel = fbk.accelerometer.reshape(1,-1)
    [d, n] = knn.kneighbors(accel, 10) # give the lines which most closely match in variable "n"
    predicted_lines = np.asanyarray(labels[n[0]], dtype=int) # obtains the label values which were predicted in "n"
    counts = np.bincount(predicted_lines) # counts each instance of face numbers
    face = np.argmax(counts) # finds the face with the highest number of instances [THIS IS OUR PREDICTION]

    return face
